"""
webcrawler_sefaz.py
--------------------

Este script fornece um exemplo de automação em Python para acessar o
Portal da Secretaria da Fazenda de Goiás (SEFAZ-GO), autenticar-se,
consultar Notas Fiscais Eletrônicas (NFE) recebidas em determinado
período e, caso existam notas, acionar o botão de download em lote.

O fluxo implementado segue os passos mapeados manualmente durante a
execução assistida por IA:

1. Acessar a página de login do portal e autenticar-se com CPF e senha.
2. Após o redirecionamento, clicar em “Acesso Restrito” e navegar até
   o serviço "Baixar XML NFE".
3. Efetuar uma segunda autenticação para a área restrita.
4. Abrir novamente o serviço "Baixar XML NFE".
5. Para cada inscrição estadual, definir o período de consulta,
   selecionar o tipo de notas (Entrada ou Saída) e realizar a pesquisa.
6. Caso haja resultados, registrar a quantidade total de notas e
   acionar o botão “Baixar todos os arquivos”, confirmando as opções
   na janela modal que se abre. O portal gera um arquivo .zip com os
   XMLs, que deve ser salvo na pasta de downloads do navegador.
7. Ao final de cada consulta, clicar em “Nova Consulta” para voltar ao
   formulário e processar a próxima inscrição estadual.

Observações:

- O script utiliza Selenium WebDriver com Chrome. É necessário ter o
  `chromedriver` instalado e compatível com a versão do navegador.
- O portal possui dois momentos de autenticação; ambos são tratados
  separadamente nas funções `login_sefaz` e `access_restricted`.
- Captchas ou outras proteções anti-bot podem impedir a automação
  integral. Em tais casos, será preciso realizar o login manualmente
  e, em seguida, deixar o script assumir a navegação.
- O ambiente de execução precisa permitir downloads automáticos. Se
  houver políticas corporativas que bloqueiem downloads (como foi
  identificado na sessão interativa), será necessário ajustá-las
  previamente ou executar o script em um ambiente sem restrições.
"""

from __future__ import annotations

import os
import time
from typing import List, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def create_driver(driver_path: str | None = None, headless: bool = False) -> webdriver.Chrome:
    """Cria e configura uma instância do Chrome WebDriver.

    :param driver_path: caminho para o executável do chromedriver. Se None,
        o Selenium tentará localizar automaticamente.
    :param headless: define se o navegador deve rodar sem interface gráfica.
    :return: instância do webdriver
    """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    # Desabilita alguns recursos que identificam automação
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(executable_path=driver_path, options=options)
    return driver


def login_sefaz(driver: webdriver.Chrome, cpf: str, senha: str) -> None:
    """Realiza o login inicial no portal SEFAZ.

    :param driver: instância do WebDriver já inicializada
    :param cpf: CPF do usuário (apenas dígitos)
    :param senha: senha do usuário
    """
    driver.get("https://portal.sefaz.go.gov.br/portalsefaz-apps/auth/login-form")
    wait = WebDriverWait(driver, 30)
    cpf_field = wait.until(EC.presence_of_element_located((By.NAME, "cpf")))
    senha_field = driver.find_element(By.NAME, "senha")
    cpf_field.clear()
    cpf_field.send_keys(cpf)
    senha_field.clear()
    senha_field.send_keys(senha)
    driver.find_element(By.XPATH, "//button[contains(., 'Autenticar')]").click()
    wait.until(EC.url_contains("/portalsefaz-apps/"))


def access_restricted(driver: webdriver.Chrome, cpf: str, senha: str) -> None:
    """Navega até a área de "Acesso Restrito" e abre o serviço de download de XML."""
    wait = WebDriverWait(driver, 30)
    restrito_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Acesso Restrito")))
    restrito_link.click()
    wait.until(lambda d: "acessoRestrito" in d.current_url)
    xml_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Baixar XML NFE")))
    xml_link.click()
    cpf_field = wait.until(EC.presence_of_element_located((By.NAME, "cpf")))
    senha_field = driver.find_element(By.NAME, "senha")
    cpf_field.clear()
    cpf_field.send_keys(cpf)
    senha_field.clear()
    senha_field.send_keys(senha)
    driver.find_element(By.XPATH, "//button[contains(., 'Autenticar')]").click()
    xml_link2 = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Baixar XML NFE")))
    xml_link2.click()


def consultar_notas(
    driver: webdriver.Chrome,
    inscricoes: List[str],
    data_inicio: str,
    data_fim: str,
    tipo: str = "Entrada",
    tempo_entre_consultas: float = 2.0,
) -> List[Tuple[str, int]]:
    """Executa consultas de notas recebidas para várias inscrições estaduais.

    :param driver: instância do WebDriver posicionada na página de consulta
    :param inscricoes: lista de inscrições estaduais a serem pesquisadas
    :param data_inicio: data inicial no formato DD/MM/AAAA
    :param data_fim: data final no formato DD/MM/AAAA
    :param tipo: "Entrada" ou "Saída". A opção "Entrada" é selecionada por padrão.
    :param tempo_entre_consultas: intervalo (segundos) para evitar ações muito rápidas
    :return: lista de tuplas contendo (inscrição, total de notas encontradas)
    """
    wait = WebDriverWait(driver, 30)
    resumo: List[Tuple[str, int]] = []
    for ie in inscricoes:
        start_input = wait.until(EC.element_to_be_clickable((By.ID, "dtInicio")))
        end_input = driver.find_element(By.ID, "dtFim")
        start_input.clear()
        start_input.send_keys(data_inicio)
        start_input.send_keys(Keys.TAB)
        end_input.clear()
        end_input.send_keys(data_fim)
        end_input.send_keys(Keys.TAB)
        ie_input = driver.find_element(By.ID, "inscricaoEstadual")
        ie_input.clear()
        ie_input.send_keys(ie)
        if tipo.lower() == "saida":
            try:
                radio_saida = driver.find_element(By.XPATH, "//label[contains(., 'Saída')]/preceding-sibling::input")
                radio_saida.click()
            except Exception:
                pass
        driver.find_element(By.XPATH, "//button[contains(., 'Pesquisar')]").click()
        time.sleep(tempo_entre_consultas)
        page_source = driver.page_source
        if "Sem Resultados" in page_source:
            resumo.append((ie, 0))
        else:
            total_div = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(., 'Total de notas:')]")))
            total_text = total_div.text.split(":")[-1].strip()
            try:
                total = int(total_text)
            except ValueError:
                total = 0
            resumo.append((ie, total))
            baixar_btn = driver.find_element(By.XPATH, "//button[contains(., 'Baixar todos os arquivos')]")
            baixar_btn.click()
            modal_baixar = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='dialog']//button[contains(., 'Baixar')]")))
            modal_baixar.click()
            # Aguarda a mensagem de conclusão na modal
            wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(., 'Concluído') and contains(@class, 'modal-body')]")))
            driver.find_element(By.XPATH, "//button[contains(., 'Ok')]").click()
        try:
            nova_consulta_btn = driver.find_element(By.XPATH, "//button[contains(., 'Nova Consulta')]")
            nova_consulta_btn.click()
        except Exception:
            driver.get(driver.current_url.split('#')[0])
        time.sleep(tempo_entre_consultas)
    return resumo


def main() -> None:
    """Exemplo de uso do webcrawler.

    Lê variáveis de ambiente `SEFAZ_CPF` e `SEFAZ_SENHA` para as
    credenciais de acesso. Define uma lista de inscrições estaduais e
    executa o fluxo de consulta. Ao final, imprime um resumo das
    quantidades de notas encontradas.
    """
    cpf = os.getenv("SEFAZ_CPF")
    senha = os.getenv("SEFAZ_SENHA")
    if not cpf or not senha:
        raise RuntimeError(
            "Defina as variáveis de ambiente SEFAZ_CPF e SEFAZ_SENHA com suas credenciais."
        )
    inscricoes = [
        "105524727",
        "103691480",
        "104094729",
        "202591182",
        "202705099",
        "202178986",
    ]
    driver = create_driver(headless=False)
    try:
        login_sefaz(driver, cpf, senha)
        access_restricted(driver, cpf, senha)
        resumo = consultar_notas(driver, inscricoes, "01/07/2025", "31/07/2025")
        for ie, total in resumo:
            print(f"IE {ie}: {total} notas encontradas")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()