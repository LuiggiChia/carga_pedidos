import os
import json
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright


def inner_playwrite(
    playwright: Playwright, dia_de_reporte: datetime, BASE_DIR: str, logger
) -> bool:

    faast_credentials_path = os.path.join(BASE_DIR, "config/faast_credentials.json")
    with open(faast_credentials_path, "r", encoding="utf-8") as file:
        faast_credentials = json.load(file)

    usuario = faast_credentials["usuario"]
    password = faast_credentials["password"]

    logger.info("Credenciales - Faast cargadas correctamente")

    fecha_inicio = dia_de_reporte.strftime("%d/%m/%Y")
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    try:

        page.goto("https://toquea.faast.pe/")
        page.set_default_timeout(90000)
        page.get_by_role("textbox", name="Nombre de Usuario").click()
        page.get_by_role("textbox", name="Nombre de Usuario").fill(usuario)
        page.get_by_role("textbox", name="Nombre de Usuario").press("Tab")
        page.get_by_role("textbox", name="Contraseña").fill(password)
        page.get_by_role("textbox", name="Contraseña").press("Enter")
        # page.goto("https://toquea.faast.pe/faast-reporting/reports#/")
        logger.info("-- Ingreso a la web")
        page.locator('[id="2"]').get_by_text("Reportes", exact=True).click()
        page.locator("a").filter(has_text="Reportes Backoffice").click()
        logger.info("-- Entro a reporte")
        page.get_by_role("listitem").filter(
            has_text="FacturacionVer Detalles"
        ).get_by_role("button").click()
        page.locator("iframe").content_frame.get_by_role(
            "textbox", name="Desde"
        ).click()
        page.locator("iframe").content_frame.get_by_role("textbox", name="Desde").fill(
            fecha_inicio
        )
        page.wait_for_timeout(10000)
        page.locator("iframe").content_frame.get_by_role(
            "textbox", name="Hasta"
        ).click()
        page.locator("iframe").content_frame.get_by_role("textbox", name="Hasta").fill(
            fecha_inicio
        )
        page.wait_for_timeout(10000)
        # Modificación
        frame = page.frame_locator("iframe")
        frame.locator("#ReportViewerControl_ctl04_ctl00").scroll_into_view_if_needed()
        frame.locator("#ReportViewerControl_ctl04_ctl00").click(force=True)
        page.wait_for_timeout(6000)
        logger.info("-- Se ve informe")
        with page.expect_download() as download_info:
            frame.get_by_role("link", name="CSV (comma delimited)").click()
        download = download_info.value
        download.save_as(f'{BASE_DIR}/{dia_de_reporte.strftime("%d_%m_%Y")}.csv')
        logger.info("-- Se guardo archivo")
        # ---------------------
        context.close()
        browser.close()
        return True
    except Exception as e:
        logger.error(f"Error durante la exportación: {e}")
        return False
    finally:
        logger.info("Finally")
        # ---------------------
        context.close()
        browser.close()


def exports_csv(dia_de_reporte: datetime, BASE_DIR: str, logger) -> bool:
    with sync_playwright() as playwright:
        return inner_playwrite(playwright, dia_de_reporte, BASE_DIR, logger)
