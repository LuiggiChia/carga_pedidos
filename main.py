import os
import json
import logging
from datetime import datetime

from src.extraction.scrapping_facturacion_faast import exports_csv
from src.processing.facturacion_processor import facturacion_processor
from src.processing.process_clients import (
    get_recent_clients_by_product,
    generate_nit_df,
    generate_client_df,
)
from src.ingestion.plantilla_carga_pedidos import (
    upload_dataframe_to_template_drive,
)
from src.utils.date_utils import get_date_of_arg
from src.utils.google_utils import (
    load_google_credentials,
    create_drive_service,
    get_report_from_drive,
    upload_file_to_drive,
)

project_path = os.path.dirname(os.path.abspath(__file__))
logs_path = os.path.join(project_path, "logs")
log_filename = f"{datetime.now().strftime('%Y%m%d')}.log"

# Credenciales del drive folder
credentials_folder_drive = os.path.join(
    project_path, "config", "credentials_folder_drive.json"
)

with open(credentials_folder_drive, "r", encoding="utf-8") as file:
    folder_drive_credentials = json.load(file)

folder_id_utils = folder_drive_credentials["folder_id_utils"]
folder_id_factoring = folder_drive_credentials["folder_id_factoring"]
folder_id_reports_factoring = folder_drive_credentials["folder_id_reports_factoring"]
folder_id_conta_clientes = folder_drive_credentials["folder_id_conta_clientes"]

# Configuraciones en general del proyecto
config_project_path = os.path.join(project_path, "config", "project_config.json")

with open(config_project_path, "r", encoding="utf-8") as file:
    config_project = json.load(file)

product = config_project["product"]

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

    # Transformar la data
    df = facturacion_processor(project_path)

    # Subir el archivo al drive
    upload_dataframe_to_template_drive(
        service=drive_service,
        df=df,
        folder_id_utils=folder_id_utils,
        folder_output_id=folder_id_factoring,
        excel_input_name="Plantilla Carga Pedidos.xlsx",
        sheet_name="Carga Pedidos",
        excel_output_name="CargaPedidos",
        logger=logger,
    )

    # Obtener Consolidado.xlsx
    file_bytes = get_report_from_drive(
        drive_service, folder_id_reports_factoring, "Consolidado.xlsx"
    )

    # Aplicar transformacion al df obtenido
    df_grouped = get_recent_clients_by_product(file_bytes, product)
    df_nit = generate_nit_df(df_grouped)
    df_carga_cliente = generate_client_df(df_grouped)

    # Subir los archivos a drive
    upload_dataframe_to_template_drive(
        service=drive_service,
        df=df_nit,
        folder_id_utils=folder_id_utils,
        folder_output_id=folder_id_conta_clientes,
        excel_input_name="CARGARDOR NIT.xlsx",
        sheet_name="Sheet1",
        excel_output_name="CargaNIT",
        logger=logger,
    )

    upload_dataframe_to_template_drive(
        service=drive_service,
        df=df_carga_cliente,
        folder_id_utils=folder_id_utils,
        folder_output_id=folder_id_conta_clientes,
        excel_input_name="Cargador Dinámico Cliente.xlsx",
        sheet_name="Fibertech",
        excel_output_name="CargaClientes",
        logger=logger,
    )
