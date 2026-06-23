import pandas as pd
from read_plantilla import escribir_plantilla_pedidos
from scrapping_facturacion_faast import exports_csv
import os
import shutil
import time
from datetime import datetime


def move_file(usuario: str, password: str):

    downloads_path = os.path.join(os.environ["USERPROFILE"], "Downloads")  # Cambiar
    destino_base = r"G:\Mi unidad\Reporteria\Data-Toquea\Factoring"  # Cambiar
    result_export = exports_csv(usuario, password)

    if result_export:
        print("Exportado correctamente")

        # 1. Ruta de Descargas
        downloads_path = os.path.join(os.environ["USERPROFILE"], "Downloads")

        # 2. Buscar el último archivo descargado (por fecha de modificación)
        archivos = [os.path.join(downloads_path, f) for f in os.listdir(downloads_path)]
        archivos = [f for f in archivos if os.path.isfile(f)]
        ultimo_archivo = max(archivos, key=os.path.getmtime)

        print(f"Último archivo descargado: {ultimo_archivo}")

        # 3. Crear ruta con formato YYYY/MM/DD
        hoy = datetime.today()
        carpeta_destino = os.path.join(destino_base, hoy.strftime("%Y%m%d"))

        os.makedirs(carpeta_destino, exist_ok=True)

        # 4. Mover archivo
        nombre_archivo = os.path.basename(ultimo_archivo)
        destino_final = os.path.join(carpeta_destino, nombre_archivo)

        time.sleep(10)
        # Copiar el archivo al destino
        shutil.copy2(ultimo_archivo, destino_final)

        time.sleep(10)

        # Eliminar el original
        os.remove(ultimo_archivo)

        print(f"Archivo movido a: {destino_final}")

        return destino_final
    else:
        print("Error durante la exportación.")
        return None


if __name__ == "__main__":

    cur = ["PEN"]
    print("Obtener recaudacion")
    # facturacion = move_file()
    facturacion = (
        r"G:\Mi unidad\Reporteria\Data-Toquea\Factoring\20251216\Facturacion.csv"
    )
    if facturacion:
        print("Recaudo obtenido con exito.")
    else:
        print("Error al obtener recaudo.")

    df = pd.read_csv(facturacion, skiprows=3)

    df = df[df["co_tipo_movimiento"].str.strip() == "GI"]

    df["articulo"] = df["descripcion"].str.split(" ").str[0]

    df["articulo"] = df["articulo"].replace(
        {
            "COMISIÓN": "S00023",
            "INTERES": "S00024",
            "GASTOS": "S00022",
        }
    )
    df["precio"] = df["moneda"].replace({"PEN": "ND-LOCAL", "USD": "ND-DOLAR"})

    df["moneda"] = df["moneda"].replace({"PEN": "L", "USD": "D"})

    df["consecutivo"] = "PFTS"
    df["campo_n"] = "N"
    df["documento"] = "F"
    df["bodega"] = "0000"
    df["condicion"] = "0"
    df["campo_nd"] = "ND"
    df["campo_vacio"] = ""
    df["campo_cero"] = 0
    df["cantidad"] = 1

    df["sub_total"] = df["sub_total"].astype(str).str.replace(",", "", regex=False)
    df["sub_total"] = pd.to_numeric(df["sub_total"], errors="coerce")

    df = df[
        [
            "nu_operacion",
            "ruc",
            "consecutivo",
            "documento",
            "campo_n",
            "bodega",
            "condicion",
            "moneda",
            "precio",
            "moneda",
            "fe_pago",
            "fe_pago",
            "fe_pago",
            "campo_nd",
            "campo_nd",
            "campo_nd",
            "campo_nd",
            "campo_nd",
            "direccion",
            "campo_vacio",
            "campo_vacio",
            "campo_vacio",
            "campo_vacio",
            "campo_vacio",
            "campo_vacio",
            "campo_vacio",
            "campo_cero",
            "campo_cero",
            "articulo",
            "cantidad",
            "sub_total",
            "campo_cero",
            "campo_cero",
            "descripcion",
            "campo_vacio",
            "campo_vacio",
            "campo_vacio",
            "campo_vacio",
            "campo_vacio",
            "campo_cero",
            "campo_vacio",
        ]
    ]

    print(df.head(10))

    escribir_plantilla_pedidos(df)
