# NF WebCrawler Quick Start

This document summarizes how to prepare the environment and run the graphical interface for downloading XML invoices from the SEFAZ portal.

## Environment Setup

1. Install **Python 3.9** or newer.
2. Download ChromeDriver that matches your Chrome version and place it on your `PATH` so the command `chromedriver --version` works.
3. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the GUI

Start the graphical interface with:
```bash
python menu.py
```
Choose the month and year for the query, provide the space‑separated list of **Inscrições Estaduais** (IEs) and pick the folder where downloads will be saved. Click **Start** to launch the crawler.

## Configurable Selectors

The CSS selectors used to locate elements on the portal are defined in `config.json`. Adjust these values if the interface changes.
