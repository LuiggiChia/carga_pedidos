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


def exports_csv(usuario: str, password: str) -> bool:

    fecha_inicio = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime(
        "%d/%m/%Y"
    )
    # fecha_inicio = '15/06/2025'

    print("inicio")
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # chrome_options.add_argument("--headless=new")  # Actívalo si no necesitas interfaz gráfica

    # Lanzar Chrome más rápido
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    try:
        # ====================
        # LOGIN
        # ====================
        driver.get("https://toquea.faast.pe/faast-reporting/reports#/")

        wait = WebDriverWait(driver, 20)

        # Esperar inputs
        wait.until(EC.presence_of_element_located((By.ID, "usuario")))

        driver.find_element(By.ID, "usuario").send_keys(usuario)
        driver.find_element(By.ID, "contraseña").send_keys(password)

        # Clic en Ingresar
        boton_ingresar = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(),'Ingresar')]")
            )
        )
        boton_ingresar.click()

        time.sleep(30)
        # Ir manualmente al módulo de reportes (manteniendo sesión)
        driver.get("https://toquea.faast.pe/faast-reporting/reports#/")

        # ====================
        # NAVEGAR A VOLUMEN OPERACIONAL
        # ====================

        # Esperar carga de lista de reportes
        li_volumen = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//li[contains(@class, 'list-group-item')][.//text()[contains(., 'Facturacion')]]",
                )
            )
        )

        # Clic en Ver Detalles
        boton = li_volumen.find_element(
            By.XPATH, ".//button[contains(text(), 'Ver Detalles')]"
        )
        driver.execute_script("arguments[0].click();", boton)

        print("Accediendo al reporte Recaudacion...")

        # ====================
        # CAMBIAR A IFRAME
        # ====================

        iframe = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//iframe[contains(@src, 'ReportServer')]")
            )
        )
        driver.switch_to.frame(iframe)

        print("Dentro del iframe del reporte.")

        # ====================
        # SETEAR FECHA DESDE (actual - 30 días)
        # ====================

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

        # ====================
        # VER INFORME
        # ====================

        boton_ver_informe = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ReportViewerControl_ctl04_ctl00"))
        )
        boton_ver_informe.click()

        print("Clic en 'Ver informe'. Esperando generación...")

        # Tiempo de espera hasta que se renderice el reporte
        time.sleep(5)  # Puede reemplazarse con espera más inteligente

        # ====================
        # EXPORTAR A CSV
        # ====================

        # Clic en el botón de exportar
        boton_exportar = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.ID, "ReportViewerControl_ctl05_ctl04_ctl00_ButtonLink")
            )
        )
        driver.execute_script("arguments[0].click();", boton_exportar)

        print("Menú de exportación desplegado.")

        # Seleccionar CSV
        opcion_csv = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(text(), 'CSV (delimitado por comas)')]")
            )
        )
        opcion_csv.click()

        time.sleep(10)

        print("Exportación completada con éxito.")

        return True

    except Exception as e:
        print(f"Error durante la exportación: {e}")
        return False

    finally:
        if "driver" in locals():
            driver.quit()


if __name__ == "__main__":
    usuario = "dany.churapa@ajegroup.com"
    password = "Faast123"

    resultado = exports_csv(usuario, password)
