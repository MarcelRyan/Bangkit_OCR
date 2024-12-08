import io
import numpy as np

from numpy.linalg import norm
from paddleocr import PaddleOCR
from PIL import Image
from datetime import datetime
from fastapi import UploadFile
from app.common.logging import logger
from app.common.database import db
from app.utils.image_utils import preprocess_image
from app.utils.llm_utils import fix_typos_and_parse
from app.utils.timestamp_utils import is_valid_timestamp
from app.models.embedding import embedding_model

# Load models and data
ocr = PaddleOCR(use_angle_cls=True, lang="en")


async def process_receipt_image(image: UploadFile, user_id: str) -> dict:
    """
    Process the receipt image and validate product information using vector search.
    Args:
        image (UploadFile): Uploaded receipt image.
        user_id (str): User identifier.
    Returns:
        dict: Processed receipt data with validation status.
    """
    try:
        logger.info("Starting receipt processing...")

        # Step 1: Read and preprocess image
        pil_image = await load_and_preprocess_image(image)

        # Step 2: Perform OCR and extract text
        extracted_text = perform_ocr(pil_image)

        # Step 3: Retrieve product data
        products = fetch_products(user_id)
        product_names = [product["product_name"] for product in products]

        # Step 4: Fix typos and parse extracted text
        structured_data = fix_typos_and_parse(extracted_text, product_names)
        data = prepare_initial_data(structured_data, user_id)

        # Step 5: Validate products using vector search
        data = validate_products(data, products)

        logger.info(f"Receipt processed successfully for user_id: {user_id}")
        return {
            "status": "success",
            "message": "Receipt processed successfully",
            "data": data,
        }
    except Exception as e:
        logger.error(f"Error processing receipt: {e}")
        return {
            "status": "failed",
            "message": "Failed to process receipt. Please try again.",
            "data": None,
        }


async def load_and_preprocess_image(image: UploadFile) -> Image:
    """Read and preprocess the uploaded image."""
    logger.info("Reading and preprocessing the uploaded image.")
    contents = await image.read()
    pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
    numpy_image = preprocess_image(pil_image)
    logger.info("Image preprocessing completed.")
    return numpy_image


def perform_ocr(image) -> list:
    """Perform OCR on the preprocessed image."""
    logger.info("Running OCR on the preprocessed image.")
    results = ocr.ocr(image, cls=True)
    extracted_text = [line[1][0] for line in results[0]]
    logger.info(f"Extracted text: {extracted_text}")
    return extracted_text


def prepare_initial_data(structured_data: dict, user_id: str) -> dict:
    """Prepare the initial receipt data structure."""
    timestamp = structured_data.get("timestamp", datetime.now().isoformat())
    if not is_valid_timestamp(timestamp):
        timestamp = datetime.now().isoformat()
    data = {
        "user_id": user_id,
        "timestamp": timestamp,
        "items": structured_data.get("items", []),
        "total_price": structured_data.get("total_price", 0),
    }
    logger.info("Initial receipt data prepared.")
    return data


def fetch_products(user_id: str) -> list:
    """
    Fetch products from a Firestore user's subcollection.

    Args:
        user_id (str): The ID of the user whose products should be fetched.

    Returns:
        list: A list of products in the user's subcollection.
    """
    try:
        products_ref = db.collection("users").document(user_id).collection("products")
        products_snapshot = products_ref.get()
        products = [
            {**product.to_dict(), "product_id": product.id}
            for product in products_snapshot
        ]

        return products

    except Exception as e:
        logger.error(f"An error occurred while fetching products: {e}")
        return []


def cosine_similarity(v1, v2):
    """Calculate cosine similarity between two vectors."""
    return np.dot(v1, v2) / (norm(v1) * norm(v2))


def validate_products(data: dict, products: list) -> dict:
    """Validate product information using local vector search."""

    logger.info("Validating products using local vector search.")
    valid_items = []
    total_price = 0

    product_embeddings = [np.array(p["embeddings"]) for p in products]

    for item in data["items"]:
        product_name = item["product_name"]
        embedding = np.array(embedding_model.embed_query(product_name))

        similarities = [
            cosine_similarity(embedding, product_embedding)
            for product_embedding in product_embeddings
        ]

        best_match_index = np.argmax(similarities)
        best_similarity = similarities[best_match_index]

        similarity_threshold = 0.5

        if best_similarity >= similarity_threshold:
            matched_product = products[best_match_index]
            item.update(
                {
                    "product_id": matched_product["product_id"],
                    "product_name": matched_product["product_name"],
                    "price_per_unit": float(matched_product["price"]),
                    "total_price": float(matched_product["price"])
                    * float(item["quantity"]),
                }
            )
            total_price += float(item["total_price"])
            valid_items.append(item)
        else:
            logger.warning(
                f"Product {product_name} has no similar match (similarity: {best_similarity}) and was removed."
            )

    data["items"] = valid_items
    data["total_price"] = total_price
    logger.info("Product validation completed.")
    return data
