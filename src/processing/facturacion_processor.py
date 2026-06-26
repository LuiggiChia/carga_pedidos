import os
import pandas as pd


def facturacion_processor_confirming(base_dir):
    raw_path = os.path.join(base_dir, "data", "raw")

    csv_file = next(f for f in os.listdir(raw_path) if f.lower().endswith(".csv"))

    csv_path = os.path.join(raw_path, csv_file)

    with open(csv_path, "r", encoding="utf-8") as f:
        num_rows = sum(1 for _ in f)

    rows_if_document_empty = 5

    rows_to_skip = 3 if num_rows >= rows_if_document_empty else 2

    df = pd.read_csv(csv_path, skiprows=rows_to_skip)

    df = df[df["co_tipo_movimiento"].str.strip() == "CF"].copy()

    df["articulo"] = df["descripcion"].str.split(" ").str[0]
    df["articulo"] = df["articulo"].replace(
        {
            "COMISIONES": "S00039",
            "INTERESES": "S00040",
        }
    )

    df["mes"] = df["descripcion"].str.lower().str.extract(
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
        expand=False,
    )

    df["sub_total"] = (
        df["sub_total"]
        .astype(str)
        .str.replace(",", "", regex=False)
    )

    df["sub_total"] = pd.to_numeric(df["sub_total"], errors="coerce")

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

    # Asignar nuevo nu_operacion para S00024
    mask_interest = df["articulo"] == "S00024"

    existing_max = pd.to_numeric(df["nu_operacion"], errors="coerce").max()
    start = int(existing_max) + 1 if not pd.isna(existing_max) else 1

    n_interest = mask_interest.sum()

    if n_interest > 0:
        df.loc[mask_interest, "nu_operacion"] = range(start, start + n_interest)

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
