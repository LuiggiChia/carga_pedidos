import os
import pandas as pd


def email_facturacion(base_dir):
    facturacion_path = os.path.join(
        base_dir, "Reports", "Faast", "output", "Facturacion"
    )

    dfs = []

    for file in os.listdir(facturacion_path):
        if file.lower().endswith(".csv"):
            csv_path = os.path.join(facturacion_path, file)
            dfs.append(pd.read_csv(csv_path, usecols=["ruc", "Textbox3"]))

    if not dfs:
        return pd.DataFrame(columns=["Cliente", "E-mail"])

    df = (
        pd.concat(dfs, ignore_index=True)
        .drop_duplicates(subset=["ruc"])
        .rename(columns={"ruc": "Cliente", "Textbox3": "E-mail"})
        .reset_index(drop=True)
    )

    return df
