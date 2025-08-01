import argparse
from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests


def parse_args():
    parser = argparse.ArgumentParser(description="Download NFE XMLs from SEFAZ portal")
    parser.add_argument("--ies", nargs="+", required=True, help="Inscricoes Estaduais")
    parser.add_argument("--start-date", required=True, help="Start date in DD/MM/YYYY")
    parser.add_argument("--end-date", required=True, help="End date in DD/MM/YYYY")
    parser.add_argument("--download-dir", default="downloads", help="Directory to store XML files")
    return parser.parse_args()


def wait_for_user(prompt: str = "Press Enter to continue..."):
    input(prompt)


def open_portal(driver: webdriver.Chrome):
    driver.get("https://portal.sefaz.go.gov.br/portalsefaz-apps/auth/login-form")
    wait_for_user("Log in manually, then press Enter to continue...")


# The selectors below are placeholders. Update them as needed when using the script.

def navigate_to_download_page(driver: webdriver.Chrome):
    """Navigate to Acesso Restrito -> Baixar XML NFE after login."""
    # click "Acesso Restrito"
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Acesso Restrito"))
    ).click()
    sleep(1)
    # click "Baixar XML NFE"
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Baixar XML NFE"))
    ).click()
    # wait for page load, re-authentication might be required
    wait_for_user("Complete any additional authentication, then press Enter...")


def set_date_range(driver: webdriver.Chrome, start_date: str, end_date: str):
    """Fill in the start and end date fields."""
    # Example selectors - adjust to match actual page
    start_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "dataInicio"))
    )
    start_field.clear()
    start_field.send_keys(start_date)
    end_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "dataFim"))
    )
    end_field.clear()
    end_field.send_keys(end_date)


def select_ie(driver: webdriver.Chrome, ie: str):
    """Enter an inscricao estadual number."""
    ie_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "inscricaoEstadual"))
    )
    ie_field.clear()
    ie_field.send_keys(ie)


def download_xmls(driver: webdriver.Chrome, base_dir: Path, ie: str, entry_type: str):
    """Click on the Entradas or Saidas option and download XMLs."""
    # entry_type should be "Entradas" or "Saidas"
    # Example radio button selector
    radio = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f"//label[contains(., '{entry_type}')]"))
    )
    radio.click()
    search_btn = driver.find_element(By.ID, "btnPesquisar")
    search_btn.click()
    sleep(2)
    # wait until table results appear
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
    )
    download_links = driver.find_elements(By.LINK_TEXT, "Baixar XML")
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
    return downloaded


def process_ie(driver: webdriver.Chrome, base_dir: Path, ie: str, start_date: str, end_date: str):
    set_date_range(driver, start_date, end_date)
    select_ie(driver, ie)
    downloads = []
    for entry_type in ("Entradas", "Saidas"):
        downloads.extend(download_xmls(driver, base_dir, ie, entry_type))
        sleep(2)
    # click "Nova Consulta" if present
    try:
        nova_consulta = driver.find_element(By.LINK_TEXT, "Nova Consulta")
        nova_consulta.click()
    except Exception:
        pass
    return downloads


def main():
    args = parse_args()
    base_dir = Path(args.download_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": str(base_dir.resolve())}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)

    try:
        open_portal(driver)
        navigate_to_download_page(driver)
        all_downloads = []
        for ie in args.ies:
            files = process_ie(driver, base_dir, ie, args.start_date, args.end_date)
            all_downloads.extend(files)
        print("\nDownloaded files:")
        for f in all_downloads:
            print(f)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
