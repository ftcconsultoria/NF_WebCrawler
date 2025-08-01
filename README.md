# NF WebCrawler

This project automates the download of electronic invoice (NFE) XML files from the SEFAZ portal. The automation relies on Selenium to drive a web browser and perform the necessary interactions while the user manually supplies credentials. It is intended to simplify the retrieval process for multiple **Inscrições Estaduais** within a specified date range.

## Required Packages

Install Python 3.9+ and ensure a suitable WebDriver (e.g., ChromeDriver) is
available on your `PATH`.  All Python dependencies are listed in the
`requirements.txt` file.

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Basic Usage

Below is a simplified snippet illustrating how Selenium can be used. It purposely omits automatic credential handling—**do not store or log your CPF or password**.

```python
from selenium import webdriver
from time import sleep

# Launch browser
browser = webdriver.Chrome()

# Open login page
browser.get("https://portal.sefaz.go.gov.br/portalsefaz-apps/auth/login-form")

# Wait for manual login
input("Log in manually, then press Enter to continue...")
```

## Manual Procedure

1. Open the login page: `https://portal.sefaz.go.gov.br/portalsefaz-apps/auth/login-form`.
2. Enter your CPF and password manually and authenticate.
3. Navigate to **"Acesso Restrito" → "Baixar XML NFE"**.
4. If asked to re-authenticate, do so manually again.
5. Set the date filter using the drop-down menus from `01/07/2025` to `31/07/2025`.
6. For each **Inscrição Estadual** from your list:
   - Enter the number.
   - Choose **"Entradas"** and download all available XMLs.
   - Select **"Saídas"** and download all XMLs as well.
   - Click **"Nova Consulta"** if another Inscrição needs to be processed.
7. Repeat the above step for every Inscrição Estadual.
8. After downloading, generate a summary that lists the paths to the downloaded files.

## Tips

- Monitor session validity: if the portal logs you out, log in again before continuing.
- Use short, human-like delays (e.g., `sleep(2)`) between actions to avoid being blocked by the site.
- Ensure downloads are complete before starting a new query.

This README provides an overview of how to set up the environment and manually operate the crawler to retrieve XML files from the SEFAZ portal.


## Interactive Mode

A small helper script `menu.py` provides an interactive way to run the crawler.
Run it with Python and follow the prompts to supply the date range and list of Inscricoes Estaduais:

```bash
python menu.py
```

Type `start` when prompted to launch the download process.

