import os
import logging
from datetime import datetime

from src.extraction.scrapping_facturacion_faast import exports_csv
from src.utils.date_utils import get_date_of_arg
from src.utils.google_utils import (
    load_google_credentials,
    create_drive_service,
    upload_file_to_drive,
)

project_path = os.path.dirname(os.path.abspath(__file__))
logs_path = os.path.join(project_path, "logs")
log_filename = f"{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(logs_path, log_filename), encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    cur = ["PEN"]
    print("Obtener Facturacion")

    # Obtener fecha
    fecha_de_reporte = get_date_of_arg()

    # Leer credenciales
    credentials = load_google_credentials(project_path, logger)
    drive_service = create_drive_service(credentials, logger)
    print(f"Procesando reporte para la fecha {fecha_de_reporte.strftime('%Y-%m-%d')}")

    # Obtener el reporte facturación de faast
    result_export = exports_csv(fecha_de_reporte, project_path, logger)

    # Subir el excel a mi drive
    upload_file_to_drive(drive_service, project_path, logger)
