import os
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

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


def get_report_from_drive(service, folder_id, file_name):
    """Search for the file inside the target folder"""

    query = (
        f"name = '{file_name}' " f"and '{folder_id}' in parents " f"and trashed = false"
    )

    results = (
        service.files()
        .list(
            q=query,
            fields="files(id)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
        .execute()
    )

    files = results.get("files", [])

    if not files:
        print(f"File '{file_name}' was not found.")
        return None

    file_id = files[0]["id"]

    file_bytes = service.files().get_media(fileId=file_id).execute()

    return file_bytes


def upload_file_to_drive(service, base_dir: str, logger):

    credentials_folder_drive = os.path.join(
        base_dir, "config", "credentials_folder_drive.json"
    )

    with open(credentials_folder_drive, "r", encoding="utf-8") as file:
        folder_drive_credentials = json.load(file)

    folder_id = folder_drive_credentials["folder_id_raw"]

    raw_path = os.path.join(base_dir, "data", "raw")

    csv_file = next(f for f in os.listdir(raw_path) if f.lower().endswith(".csv"))

    file_path = os.path.join(raw_path, csv_file)

    media = MediaFileUpload(file_path, mimetype="text/csv")

    file = (
        service.files()
        .create(
            body={"name": csv_file, "parents": [folder_id]},
            media_body=media,
            fields="id,name",
            supportsAllDrives=True,
        )
        .execute()
    )

    logger.info(f"Subido: {file['name']}")
    logger.info(f"ID: {file['id']}")

    return file["id"]
