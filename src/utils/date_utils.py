import argparse
from datetime import datetime, timedelta


def get_date_of_arg():
    parser = argparse.ArgumentParser(description="Proceso de facturación FAAST")

    parser.add_argument(
        "--day",
        type=str,
        required=False,
        help="Fecha del reporte en formato YYYY/MM/DD",
    )

    args = parser.parse_args()

    if args.day:
        try:
            print(f"dia de hoy {args.day}")
            selectedDay = datetime.strptime(args.day, "%Y/%m/%d")
        except ValueError:
            raise ValueError("Formato de fecha inválido. Usar YYYY/MM/DD")
    else:
        selectedDay = datetime.today() - timedelta(days=1)

    return selectedDay
