from google.oauth2 import service_account
from google.cloud import firestore
from app.common.config import settings


credentials = service_account.Credentials.from_service_account_file(
    settings.firebase_credentials
)

db = firestore.Client(
    project=settings.project_id,
    database=settings.database,
    credentials=credentials,
)
