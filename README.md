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
   > **Note:** The portal may ask for your credentials again here. The crawler
   will pause and display a **Continuar** dialog; log in and click the button to
   resume.
4. If asked to re-authenticate, do so manually again.
5. Set the date filter using the drop-down menus from `01/07/2025` to `31/07/2025`.
6. For each **Inscrição Estadual** from your list:
   - Enter the number.
   - Choose **"Entradas"** and download all available XMLs.
   - Select **"Saídas"** and download all XMLs as well.
   - Click **"Nova Consulta"** if another Inscrição needs to be processed.
7. Repeat the above step for every Inscrição Estadual.
8. After downloading, generate a summary that lists the paths to the downloaded files.

## Updating Selectors

Elements such as **Acesso Restrito** and **Baixar XML NFE** are located using CSS
and text selectors defined in a configuration file, `config.json`. If the script
fails to locate a menu option or form field, inspect the page manually and
update the appropriate selector in `config.json`.

### `config.json` format

```json
{
  "navigate_to_download_page": {
    "acesso_selector": "a.dashboard-sistemas-item[title='Acessar o Sistema']",
    "baixar_xml_link": "Baixar XML NFE"
  },
  "set_date_range": {
    "start_id": "dataInicio",
    "end_id": "dataFim"
  },
  "select_ie": {
    "field_id": "inscricaoEstadual"
  },
  "download_xmls": {
    "search_button_id": "btnPesquisar",
    "table_selector": "table",
    "download_link_text": "Baixar XML"
  }
}
```

Each section corresponds to a function in `crawler.py` and can be adjusted to
match the HTML structure of the portal. If `config.json` is missing, the default
selectors coded in `crawler.py` are used.

## Tips

- Monitor session validity: if the portal logs you out, log in again before continuing.
- Short, human-like delays are automatically added between actions to reduce the chance of being blocked by the site.
- Ensure downloads are complete before starting a new query.

This README provides an overview of how to set up the environment and manually operate the crawler to retrieve XML files from the SEFAZ portal.


## Interactive Mode

The `menu.py` script now launches a small graphical interface similar to a Windows
application. Choose the month and year, enter the space-separated list of
**Inscrições Estaduais** and select the download directory (use the **Browse**
button) then click **Start**.

While the automation is running, moving the mouse over the application window
pauses execution. After a few seconds without movement, the process resumes
where it stopped.

When manual interaction is required (for instance, to log in on the portal), a
small dialog appears asking you to "Continuar". After completing the step,
click the button to resume the crawler.

Run the menu with Python:

```bash
python menu.py
```

