import datetime
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def exports_csv(usuario: str, password: str) -> bool:

    fecha_inicio = (
        datetime.datetime.now() - datetime.timedelta(days=1)
    ).strftime("%d/%m/%Y")

    print("inicio")

    download_dir = Path("data/raw").resolve()
    download_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        context = browser.new_context(
            accept_downloads=True,
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        page = context.new_page()

        try:
            # ====================
            # LOGIN
            # ====================

            page.goto("https://toquea.faast.pe/faast-reporting/reports#/", wait_until="networkidle")

            page.wait_for_selector("#usuario", timeout=20_000)

            page.fill("#usuario", usuario)
            page.fill("#contraseña", password)

            page.click("//button[contains(text(),'Ingresar')]")

            # Espera explícita: que aparezca algún elemento del dashboard
            # en lugar de un sleep fijo de 30 segundos
            page.wait_for_selector(
                "li.list-group-item",
                timeout=40_000,
                state="visible",
            )

            print("Login exitoso, dashboard cargado.")

            # ====================
            # REPORTE FACTURACION
            # ====================

            li_volumen = page.locator(
                "li.list-group-item",
                has=page.locator("text=Facturacion"),
            ).first

            li_volumen.wait_for(state="visible", timeout=20_000)

            boton = li_volumen.locator("button", has_text="Ver Detalles")
            boton.scroll_into_view_if_needed()
            boton.click()

            print("Accediendo al reporte Facturacion...")

            # Esperar el iframe con el ReportServer
            iframe_element = page.wait_for_selector(
                "//iframe[contains(@src, 'ReportServer')]",
                timeout=20_000,
            )

            frame = iframe_element.content_frame()

            print("Dentro del iframe del reporte.")

            # Setear la fecha de inicio directamente vía JS (igual que en Selenium)
            frame.wait_for_selector(
                "#ReportViewerControl_ctl04_ctl03_txtValue",
                timeout=15_000,
            )

            frame.evaluate(
                "document.getElementById('ReportViewerControl_ctl04_ctl03_txtValue').value = arguments[0];",
                fecha_inicio,
            )

            print(f"Fecha desde seteada a: {fecha_inicio}")

            frame.click(
                "#ReportViewerControl_ctl04_ctl00",
                timeout=10_000,
            )

            print("Clic en 'Ver informe'. Esperando generación...")

            frame.wait_for_timeout(5_000)

            # Desplegar menú de exportación
            frame.click(
                "#ReportViewerControl_ctl05_ctl04_ctl00_ButtonLink",
                timeout=20_000,
            )

            print("Menú de exportación desplegado.")

            # Iniciar descarga esperando el evento de download
            with page.expect_download(timeout=30_000) as download_info:
                frame.click(
                    "//a[contains(text(), 'CSV (delimitado por comas)')]",
                    timeout=10_000,
                )

            download = download_info.value

            # Guardar el archivo en la carpeta destino conservando el nombre original
            dest = download_dir / download.suggested_filename
            download.save_as(dest)

            print(f"Archivo descargado en: {dest}")
            print("Exportación completada con éxito.")

            return True

        except PlaywrightTimeoutError as e:
            print("=" * 80)
            print("TIPO: PlaywrightTimeoutError")
            print("ERROR:", repr(e))
            print("=" * 80)

            # Diagnóstico: screenshot + HTML para saber en qué pantalla falló
            try:
                page.screenshot(path="debug_error.png", full_page=True)
                Path("debug_page.html").write_text(page.content(), encoding="utf-8")
                print("Screenshot guardado en debug_error.png")
                print("HTML guardado en debug_page.html")
            except Exception:
                pass

            traceback.print_exc()
            return False

        except Exception as e:
            print("=" * 80)
            print("TIPO:", type(e).__name__)
            print("ERROR:", repr(e))
            print("=" * 80)

            try:
                page.screenshot(path="debug_error.png", full_page=True)
                Path("debug_page.html").write_text(page.content(), encoding="utf-8")
            except Exception:
                pass

            traceback.print_exc()
            return False

        finally:
            context.close()
            browser.close()