import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive"]


def load_google_credentials(base_dir: str, logger):
    logger.info("Cargando credenciales de Google")

    credentials_path = os.path.join(base_dir, "config/credentials.json")

    with open(credentials_path, "r") as file:
        credentials_data = json.load(file)

    logger.info("Credenciales cargadas correctamente")

    return Credentials.from_service_account_info(credentials_data, scopes=SCOPES)


def create_drive_service(credentials, logger):
    logger.info("Creando servicio de Google Drive")

    service = build("drive", "v3", credentials=credentials)

    logger.info("Servicio de Google Drive creado")

    return service


def create_folder(service, folder_name: str, logger):
    logger.info(f"Creando carpeta: {folder_name}")

    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }

    folder = service.files().create(body=folder_metadata, fields="id,name").execute()

    logger.info(f"Carpeta creada correctamente. ID: {folder['id']}")

    return folder["id"]
