from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
from pathlib import Path


def exports_csv(usuario: str, password: str) -> bool:

    fecha_inicio = (
        datetime.datetime.now() - datetime.timedelta(days=1)
    ).strftime("%d/%m/%Y")

    print("inicio")

    # Carpeta de descarga del proyecto
    download_dir = Path("data/raw").resolve()
    download_dir.mkdir(parents=True, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    prefs = {
        "download.default_directory": str(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }

    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
    )

    try:
        # ====================
        # LOGIN
        # ====================

        driver.get("https://toquea.faast.pe/faast-reporting/reports#/")

        wait = WebDriverWait(driver, 20)

        wait.until(EC.presence_of_element_located((By.ID, "usuario")))

        driver.find_element(By.ID, "usuario").send_keys(usuario)
        driver.find_element(By.ID, "contraseña").send_keys(password)

        boton_ingresar = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(),'Ingresar')]")
            )
        )
        boton_ingresar.click()

        time.sleep(30)

        driver.get("https://toquea.faast.pe/faast-reporting/reports#/")

        # ====================
        # REPORTE FACTURACION
        # ====================

        li_volumen = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//li[contains(@class, 'list-group-item')][.//text()[contains(., 'Facturacion')]]",
                )
            )
        )

        boton = li_volumen.find_element(
            By.XPATH,
            ".//button[contains(text(), 'Ver Detalles')]",
        )

        driver.execute_script("arguments[0].click();", boton)

        print("Accediendo al reporte Facturacion...")

        iframe = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//iframe[contains(@src, 'ReportServer')]")
            )
        )

        driver.switch_to.frame(iframe)

        print("Dentro del iframe del reporte.")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.ID, "ReportViewerControl_ctl04_ctl03_txtValue")
            )
        )

        driver.execute_script(
            "document.getElementById('ReportViewerControl_ctl04_ctl03_txtValue').value = arguments[0];",
            fecha_inicio,
        )

        print(f"Fecha desde seteada a: {fecha_inicio}")

        boton_ver_informe = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.ID, "ReportViewerControl_ctl04_ctl00")
            )
        )

        boton_ver_informe.click()

        print("Clic en 'Ver informe'. Esperando generación...")

        time.sleep(5)

        boton_exportar = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.ID, "ReportViewerControl_ctl05_ctl04_ctl00_ButtonLink")
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            boton_exportar,
        )

        print("Menú de exportación desplegado.")

        opcion_csv = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(text(), 'CSV (delimitado por comas)')]",
                )
            )
        )

        opcion_csv.click()

        time.sleep(10)

        print(f"Archivo descargado en: {download_dir}")
        print("Exportación completada con éxito.")

        return True

    except Exception as e:
        print(f"Error durante la exportación: {e}")
        return False

    finally:
        driver.quit()
if __name__ == "__main__":
    usuario = "dany.churapa@ajegroup.com"
    password = "Faast123"

    resultado = exports_csv(usuario, password)
