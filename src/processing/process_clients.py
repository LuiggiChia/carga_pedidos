import io
import datetime
import pandas as pd

# from read_plantilla import escribir_plantilla_nit, escribir_plantilla_clientes


def get_recent_clients_by_product(file_bytes, product: str):
    yesterday = datetime.datetime.now() - datetime.timedelta(days=3)
    yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
    print(df.head())
    print(df.columns)

    df = df[df["producto"] == product]

    grouped = (
        df.groupby(["rut_cliente", "razon_social_cliente"])
        .agg(fecha_giro=("fecha_giro", "min"))
        .reset_index()
    )

    grouped = grouped.loc[grouped["fecha_giro"] >= yesterday]

    return grouped


def generate_nit_df(grouped):
    result = grouped[["rut_cliente", "razon_social_cliente"]].copy()

    result["rut_cliente"] = result["rut_cliente"].astype(str).str.strip()
    result["razon_social_cliente"] = (
        result["razon_social_cliente"].astype(str).str.strip()
    )
    result["Tipo"] = "RUC"
    result["Activo"] = "S"

    result = result.rename(
        columns={"rut_cliente": "NIT", "razon_social_cliente": "Nombre"}
    )
    result = result.drop_duplicates(subset="NIT").reset_index(drop=True)

    print("NIT DataFrame generated with", len(result), "unique NITs.")

    return result


def generate_client_df(grouped):
    clientes = grouped["rut_cliente"].astype(str).str.strip()
    nombre = grouped["razon_social_cliente"].astype(str).str.strip()
    alias = nombre.copy()
    contribuyente = clientes.copy()

    yesterday = pd.Timestamp.today().normalize() - pd.Timedelta(days=1)
    fecha_ingreso = pd.Series([yesterday] * len(grouped), index=grouped.index)

    result = pd.DataFrame(
        {
            "Cliente": clientes,
            "Nombre": nombre,
            "Detalle Dirección": "",
            "Alias": alias,
            "Contacto": "",
            "Cargo": "",
            "Dirección": "",
            "Dirección de Embarque": "",
            "Teléfono 1": "",
            "Teléfono 2": "",
            "Fáx": "",
            "Contribuyente": contribuyente,
            "Fecha Ingreso": fecha_ingreso,
            "Multimoneda": "S",
            "Moneda": "S",
            "Saldo": "",
            "Saldo Local": "",
            "Saldo Dólar": "",
            "Saldo Crédito": "",
            "Saldo No Cargos": "",
            "Límite Crédito": "",
            "Exceder Límite": "",
            "Interés": "",
            "Interés Mora": "",
            "Última Mora": "",
            "Último Movimiento": "",
            "Condición Pago": "30CR",
            "Nivel Precio": "ND-LOCAL",
            "Descuento": "",
            "Moneda Nivel": "",
            "Backorder": "",
            "País": "PER",
            "Zona": "ND",
            "Ruta": "",
            "Vendedor": "ND",
            "Cobrador": "ND",
            "Acepta Fracciones": "",
            "Activo": "",
            "Exento Impuesto": "",
            "Impuesto 1": "",
            "Impuesto 2": "",
            "Cobro Judicial": "",
            "Categoría Cliente": "CL_TERC",
            "Clase ABC": "",
            "Días Abastecimiento": "",
            "Usa Tarjeta": "",
            "Tarjeta Crédito": "",
            "Tipo Tarjeta": "",
            "Vencimiento Tarjeta": "",
            "E-mail": "",
            "Requiere Orden Compra": "",
            "Es Corporación": "",
            "Cliente Corporación": "",
            "Registra Documentos en la Corp": "",
            "Usa Dirección de Embarque de Corp": "",
        }
    )
    result = result.drop_duplicates(subset="Cliente").reset_index(drop=True)

    print("Client DataFrame generated with", len(result), "unique Clients.")

    return result
