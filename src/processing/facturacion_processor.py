import os
import pandas as pd


def facturacion_processor_confirming(base_dir):

    month_map = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }

    raw_path = os.path.join(base_dir, "data", "raw")

    csv_file = next(f for f in os.listdir(raw_path) if f.lower().endswith(".csv"))

    csv_path = os.path.join(raw_path, csv_file)

    with open(csv_path, "r", encoding="utf-8") as f:
        num_rows = sum(1 for _ in f)

    rows_if_document_empty = 5

    rows_to_skip = 3 if num_rows >= rows_if_document_empty else 2

    df = pd.read_csv(csv_path, skiprows=rows_to_skip)

    # Filtrar Confirming
    df = df[df["co_tipo_movimiento"].str.strip() == "CF"].copy()
    print("Reporte de Confirming")
    print(df.head())

    # Obtener artículo
    df["articulo"] = df["descripcion"].str.split().str[0]
    df["articulo"] = df["articulo"].replace(
        {
            "COMISIONES": "S00040",
            "INTERESES": "S00039",
        }
    )

    # Obtener mes
    df["mes"] = df["descripcion"].str.lower().str.extract(
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
        expand=False,
    )

    # Limpiar subtotal
    df["sub_total"] = (
        df["sub_total"]
        .astype(str)
        .str.replace(",", "", regex=False)
    )

    df["sub_total"] = pd.to_numeric(df["sub_total"], errors="coerce")

    # Agrupar
    df = (
        df.groupby(
            [
                "fe_pago",
                "ruc",
                "moneda",
                "mes",
                "articulo",
            ],
            as_index=False,
        )
        .agg(
            {
                "sub_total": "sum",
                "descripcion": "first",
                "direccion": "first",
                "nu_operacion": "first",
            }
        )
    )

    # ==========================================
    # NUEVA LÓGICA PARA nu_operacion
    # ==========================================

    # Extraer el día de la descripción
    df["dia"] = (
        df["descripcion"]
        .str.extract(r"CONFIRMING\s+(\d+)", expand=False)
        .astype(int)
    )

    # Obtener el menor día por mes
    dias_por_mes = (
        df.groupby("mes", as_index=False)["dia"]
        .min()
    )

    # Ordenar meses
    dias_por_mes["mes_num"] = dias_por_mes["mes"].map(month_map)
    dias_por_mes = dias_por_mes.sort_values("mes_num")

    # El número inicial será el día del primer mes
    numero_inicial = dias_por_mes["dia"].iloc[0]

    # Asignar número de operación consecutivo por mes
    dias_por_mes["nu_operacion"] = range(
        numero_inicial,
        numero_inicial + len(dias_por_mes)
    )

    # Reemplazar nu_operacion
    df = df.drop(columns=["nu_operacion"])

    df = df.merge(
        dias_por_mes[["mes", "nu_operacion"]],
        on="mes",
        how="left",
    )

    # ==========================================
    # Completar columnas
    # ==========================================

    df["precio"] = df["moneda"].replace(
        {
            "PEN": "ND-LOCAL",
            "USD": "ND-DOLAR",
        }
    )

    df["moneda"] = df["moneda"].replace(
        {
            "PEN": "L",
            "USD": "D",
        }
    )

    df["consecutivo"] = "PFTS"
    df["campo_n"] = "N"
    df["documento"] = "F"
    df["bodega"] = "0000"
    df["condicion"] = "0"
    df["campo_nd"] = "ND"
    df["campo_vacio"] = ""
    df["campo_cero"] = 0
    df["cantidad"] = 1

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

    return df


def facturacion_processor_factoring(base_dir):
    raw_path = os.path.join(base_dir, "data", "raw")

    csv_file = next(f for f in os.listdir(raw_path) if f.lower().endswith(".csv"))

    csv_path = os.path.join(raw_path, csv_file)

    with open(csv_path, "r", encoding="utf-8") as f:
        num_rows = sum(1 for _ in f)

    rows_if_document_empty = 5

    rows_to_skip = 3 if num_rows >= rows_if_document_empty else 2

    df = pd.read_csv(csv_path, skiprows=rows_to_skip)

    df = df[df["co_tipo_movimiento"].str.strip() == "GI"]

    df["articulo"] = df["descripcion"].str.split(" ").str[0]

    df["articulo"] = df["articulo"].replace(
        {
            "COMISIÓN": "S00023",
            "COMISION": "S00023",
            "INTERES": "S00024",
            "GASTOS": "S00022",
        }
    )

    # assign unique numeric nu_operacion for INTERES (S00024)
    mask_interest = df["articulo"] == "S00024"

    # Convert existing nu_operacion to numeric where possible and get max
    existing_max = pd.to_numeric(df["nu_operacion"], errors="coerce").max()
    start = int(existing_max) + 1 if not pd.isna(existing_max) else 1

    # Number of INTERES rows
    n_interest = int(mask_interest.sum())
    if n_interest > 0:
        new_nums = list(range(start, start + n_interest))
        # Preserve index order when assigning
        df.loc[mask_interest, "nu_operacion"] = pd.Series(
            new_nums, index=df.loc[mask_interest].index
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
    return df
