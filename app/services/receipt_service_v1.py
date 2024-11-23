from paddleocr import PaddleOCR
from PIL import Image
import io
from datetime import datetime
from fastapi import UploadFile
from app.common.logging import logger
from app.utils.image_utils import preprocess_image

ocr = PaddleOCR(use_angle_cls=True, lang="en")


async def process_receipt_image(image: UploadFile, user_id: str) -> dict:
    try:
        logger.info("Starting receipt processing...")

        # Step 1: Read the uploaded image
        logger.info("Reading the uploaded image.")
        contents = await image.read()
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
        logger.info("Image successfully loaded into PIL.")

        # Step 2: Preprocess the image
        logger.info("Preprocessing the image.")
        numpy_image = preprocess_image(pil_image)
        logger.info("Image preprocessing completed.")

        # Step 3: Perform OCR
        logger.info("Running OCR on the preprocessed image.")
        results = ocr.ocr(numpy_image, cls=True)
        logger.info("OCR processing completed.")

        # Step 4: Extract text from OCR results
        logger.info("Extracting text from OCR results.")
        extracted_text = []
        for line in results[0]:
            extracted_text.append(line[1][0])
        logger.info(f"Extracted text: {extracted_text}")

        # TODO: Postprocess OCR Text
        data = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "total_price": 125000,
            "items": [
                {
                    "product_id": "prod_001",
                    "product_name": "Nasi Goreng Spesial",
                    "quantity": 2,
                    "price_per_unit": 25000,
                    "total_price": 50000,
                },
                {
                    "product_id": "prod_002",
                    "product_name": "Es Teh Manis",
                    "quantity": 3,
                    "price_per_unit": 10000,
                    "total_price": 30000,
                },
                {
                    "product_id": "prod_003",
                    "product_name": "Ayam Bakar",
                    "quantity": 1,
                    "price_per_unit": 45000,
                    "total_price": 45000,
                },
            ],
        }
        logger.info("Receipt data successfully created.")

        # Return success response
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
