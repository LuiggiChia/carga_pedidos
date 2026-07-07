import os
import json
import shutil
import logging
from datetime import datetime, timedelta

from src.extraction.scrapping_facturacion_faast import exports_csv
from src.processing.facturacion_processor import (
    facturacion_processor_factoring,
    facturacion_processor_confirming
)
from src.processing.email_from_facturacion import (
    email_facturacion
)
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
raw_data_path = os.path.join(project_path, "data/raw")
bronze_data_path = os.path.join(project_path, "data/bronze")
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
project_date = config_project["project_date"]

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

    # Obtener fecha
    if not project_date:
        fecha_de_reporte = get_date_of_arg()
    else:
        fecha_de_reporte = datetime.strptime(project_date, "%d/%m/%Y") - timedelta(days=1)
    print(f"Fecha Reporte: {fecha_de_reporte}")

    # Leer credenciales
    credentials = load_google_credentials(project_path, logger)
    drive_service = create_drive_service(credentials, logger)
    print(f"Procesando reporte para la fecha {fecha_de_reporte.strftime('%Y-%m-%d')}")

    # Obtener el reporte facturación de faast
    result_export = exports_csv(fecha_de_reporte, project_path, logger)

    # Subir el excel a mi drive
    upload_file_to_drive(drive_service, project_path, logger)

    # Transformar la data
    df_factoring = facturacion_processor_factoring(project_path)
    df_confirming = facturacion_processor_confirming(project_path)

    # Subir el archivo al drive
    if not df_factoring.empty:
        upload_dataframe_to_template_drive(
            service=drive_service,
            df=df_factoring,
            folder_id_utils=folder_id_utils,
            folder_output_id=folder_id_factoring,
            excel_input_name="Plantilla Carga Pedidos.xlsx",
            sheet_name="Carga Pedidos",
            excel_output_name="CargaPedidosFactoring",
            logger=logger,
            day_of_report=fecha_de_reporte
        )

    if not df_confirming.empty:
        upload_dataframe_to_template_drive(
            service=drive_service,
            df=df_confirming,
            folder_id_utils=folder_id_utils,
            folder_output_id=folder_id_factoring,
            excel_input_name="Plantilla Carga Pedidos.xlsx",
            sheet_name="Carga Pedidos",
            excel_output_name="CargaPedidosConfirming",
            logger=logger,
            day_of_report=fecha_de_reporte
        )

    # Mover archivo archivo csv
    csv_file = next(f for f in os.listdir(raw_data_path) if f.lower().endswith(".csv"))
    shutil.move(
        os.path.join(raw_data_path, csv_file),
        os.path.join(bronze_data_path, csv_file),
    )

    # Obtener Consolidado.xlsx
    file_bytes = get_report_from_drive(
        drive_service, folder_id_reports_factoring, "Consolidado.xlsx"
    )

    # Aplicar transformacion al df obtenido
    df_grouped = get_recent_clients_by_product(file_bytes, product)
    df_nit = generate_nit_df(df_grouped)
    df_carga_cliente = generate_client_df(df_grouped)
    df_email_facturacion = email_facturacion(bronze_data_path)
    print(df_carga_cliente.head())
    print(df_email_facturacion)

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
