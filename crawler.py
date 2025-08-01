import argparse
import json
import random
from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests

from pause import PauseController
from typing import Callable, Optional


CONFIG_PATH = Path(__file__).with_name("config.json")
try:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        SELECTORS = json.load(f)
except Exception:
    SELECTORS = {}


pause_controller: Optional[PauseController] = None
prompt_callback: Optional[Callable[[str], None]] = None


def set_pause_controller(controller: PauseController):
    global pause_controller
    pause_controller = controller


def set_prompt_callback(callback: Callable[[str], None]):
    """Set a callback to display interactive prompts."""
    global prompt_callback
    prompt_callback = callback


def check_pause():
    if pause_controller:
        pause_controller.check()


def human_delay(min_sec: float = 0.5, max_sec: float = 1.5):
    check_pause()
    sleep(random.uniform(min_sec, max_sec))


def parse_args(arg_list=None):
    parser = argparse.ArgumentParser(description="Download NFE XMLs from SEFAZ portal")
    parser.add_argument("--ies", nargs="+", required=True, help="Inscricoes Estaduais")
    parser.add_argument("--start-date", required=True, help="Start date in DD/MM/YYYY")
    parser.add_argument("--end-date", required=True, help="End date in DD/MM/YYYY")
    parser.add_argument("--download-dir", default="downloads", help="Directory to store XML files")
    return parser.parse_args(arg_list)


def wait_for_user(prompt: str = "Press Enter to continue..."):
    """Pause execution until the user confirms via console or GUI."""
    if prompt_callback:
        prompt_callback(prompt)
    else:
        input(prompt)


def close_certificate_popup(driver: webdriver.Chrome):
    """Dismiss the certificate selection popup if it appears."""
    try:
        # Some browsers open the certificate dialog in a new window.
        WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))
        main = driver.current_window_handle
        for handle in driver.window_handles:
            if handle != main:
                driver.switch_to.window(handle)
                driver.close()
                driver.switch_to.window(main)
                human_delay()
                break
    except Exception:
        pass
    # Fallback for JavaScript alerts
    try:
        WebDriverWait(driver, 2).until(EC.alert_is_present())
        driver.switch_to.alert.dismiss()
        human_delay()
    except Exception:
        pass


def open_portal(driver: webdriver.Chrome):
    check_pause()
    driver.get("https://portal.sefaz.go.gov.br/portalsefaz-apps/auth/login-form")
    close_certificate_popup(driver)
    wait_for_user("Log in manually, then press Enter to continue...")


# The selectors below are placeholders. Update them as needed when using the script.

def navigate_to_download_page(driver: webdriver.Chrome):
    """Navigate to Acesso Restrito -> Baixar XML NFE after login."""
    check_pause()
    cfg = SELECTORS.get("navigate_to_download_page", {})
    acesso_selector = cfg.get(
        "acesso_selector",
        "a.dashboard-sistemas-item[title='Acessar o Sistema']",
    )
    acesso = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, acesso_selector))
    )
    acesso.click()
    human_delay(1, 2)
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[-1])
    baixar_text = cfg.get("baixar_xml_link", "Baixar XML NFE")
    try:
        baixar_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, baixar_text))
        )
        existing_handles = driver.window_handles[:]
        driver.execute_script("arguments[0].click();", baixar_link)
        if len(driver.window_handles) > len(existing_handles):
            driver.switch_to.window(driver.window_handles[-1])
    except TimeoutException:
        print(
            "Could not locate the 'Baixar XML NFE' link. The selector may be outdated."
        )
        print(f"Current URL: {driver.current_url}")
        try:
            screenshot = "navigate_error.png"
            if driver.save_screenshot(screenshot):
                print(f"Screenshot saved to {screenshot}")
        except Exception:
            pass
        return
    human_delay(0.5, 1.5)
    # wait for page load, re-authentication might be required
    wait_for_user("Complete any additional authentication, then press Enter...")


def set_date_range(driver: webdriver.Chrome, start_date: str, end_date: str):
    """Fill in the start and end date fields."""
    # Example selectors - adjust to match actual page
    check_pause()
    cfg = SELECTORS.get("set_date_range", {})
    start_id = cfg.get("start_id", "dataInicio")
    end_id = cfg.get("end_id", "dataFim")
    start_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, start_id))
    )
    start_field.clear()
    start_field.send_keys(start_date)
    end_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, end_id))
    )
    end_field.clear()
    end_field.send_keys(end_date)
    human_delay()


def select_ie(driver: webdriver.Chrome, ie: str):
    """Enter an inscricao estadual number."""
    check_pause()
    cfg = SELECTORS.get("select_ie", {})
    field_id = cfg.get("field_id", "inscricaoEstadual")
    ie_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, field_id))
    )
    ie_field.clear()
    ie_field.send_keys(ie)
    human_delay()


def download_xmls(driver: webdriver.Chrome, base_dir: Path, ie: str, entry_type: str):
    """Click on the Entradas or Saidas option and download XMLs."""
    # entry_type should be "Entradas" or "Saidas"
    # Example radio button selector
    check_pause()
    cfg = SELECTORS.get("download_xmls", {})
    radio = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f"//label[contains(., '{entry_type}')]"))
    )
    radio.click()
    human_delay()
    search_btn_id = cfg.get("search_button_id", "btnPesquisar")
    search_btn = driver.find_element(By.ID, search_btn_id)
    search_btn.click()
    human_delay(1, 2)
    # wait until table results appear
    table_selector = cfg.get("table_selector", "table")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, table_selector))
    )
    link_text = cfg.get("download_link_text", "Baixar XML")
    download_links = driver.find_elements(By.LINK_TEXT, link_text)
    ie_dir = base_dir / ie / entry_type
    ie_dir.mkdir(parents=True, exist_ok=True)
    downloaded = []
    # Preserve session cookies so requests can access authenticated resources
    cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
    for link in download_links:
        file_url = link.get_attribute("href")
        filename = file_url.split("/")[-1]
        dest = ie_dir / filename
        resp = requests.get(file_url, cookies=cookies)
        if resp.ok:
            with open(dest, "wb") as f:
                f.write(resp.content)
            downloaded.append(dest)
        human_delay(0.5, 1)
    return downloaded


def process_ie(driver: webdriver.Chrome, base_dir: Path, ie: str, start_date: str, end_date: str):
    set_date_range(driver, start_date, end_date)
    select_ie(driver, ie)
    downloads = []
    for entry_type in ("Entradas", "Saidas"):
        downloads.extend(download_xmls(driver, base_dir, ie, entry_type))
        human_delay(1, 2)
    # click "Nova Consulta" if present
    try:
        nova_consulta = driver.find_element(By.LINK_TEXT, "Nova Consulta")
        nova_consulta.click()
    except Exception:
        pass
    return downloads


def main(arg_list=None):
    args = parse_args(arg_list)
    base_dir = Path(args.download_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": str(base_dir.resolve())}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    # Start the browser in fullscreen mode
    try:
        driver.maximize_window()
    except Exception:
        pass

    try:
        open_portal(driver)
        navigate_to_download_page(driver)
        all_downloads = []
        for ie in args.ies:
            files = process_ie(driver, base_dir, ie, args.start_date, args.end_date)
            all_downloads.extend(files)
            check_pause()
        print("\nDownloaded files:")
        for f in all_downloads:
            print(f)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
