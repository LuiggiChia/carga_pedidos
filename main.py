import os
import json

from src.extraction.scrapping_facturacion_faast import exports_csv


project_path = os.path.dirname(os.path.abspath(__file__))
credentials_path = os.path.join(project_path, "config",
                                "faast_credentials.json")

with open(credentials_path, "r", encoding="utf-8") as file:
    faast_credentials = json.load(file)
usuario = faast_credentials["usuario"]
password = faast_credentials["password"]

downloads_path = os.path.join(os.environ["USERPROFILE"], "Downloads")

print(downloads_path)