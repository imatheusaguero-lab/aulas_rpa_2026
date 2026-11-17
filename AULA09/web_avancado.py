"""Lab 09 - Dropdowns, alerts, iframes e múltiplas janelas com Selenium.

Regras: sem time.sleep(); usar WebDriverWait + expected_conditions,
validar as ações com assert e registrar as etapas com logging.
"""

import logging
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


# Constantes: dados que não mudam durante a execução.
RA = "6326149"
TEMPO_ESPERA = 15
PASTA_SCRIPT = Path(__file__).resolve().parent
ARQUIVO_LOG = PASTA_SCRIPT / "web_avancado.log"

URL_DROPDOWN = "https://the-internet.herokuapp.com/dropdown"
URL_ALERTS = "https://the-internet.herokuapp.com/javascript_alerts"
URL_IFRAME = "https://the-internet.herokuapp.com/iframe"
URL_WINDOWS = "https://the-internet.herokuapp.com/windows"

logger = logging.getLogger("lab09")


def configurar_logs():
    """Envia INFO+ ao terminal e DEBUG+ ao arquivo de log."""
    logger.setLevel(logging.DEBUG)
    if logger.handlers:
        return

    formato = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s"
    )

    # StreamHandler: exibe os eventos importantes no terminal.
    terminal = logging.StreamHandler()
    terminal.setLevel(logging.INFO)
    terminal.setFormatter(formato)

    # FileHandler: grava um histórico mais detalhado ao lado do script.
    arquivo = logging.FileHandler(ARQUIVO_LOG, encoding="utf-8")
    arquivo.setLevel(logging.DEBUG)
    arquivo.setFormatter(formato)

    logger.addHandler(terminal)
    logger.addHandler(arquivo)


def parte_1_selects(driver):
    """Lista as opções e seleciona Option 2 obrigatoriamente por índice."""
    logger.info("PARTE 1 | Iniciando dropdown.")
    driver.get(URL_DROPDOWN)
    espera = WebDriverWait(driver, TEMPO_ESPERA)

    # CSS Selector: procura o elemento HTML <select> da página.
    # Exemplo: <select id="dropdown">...</select> → WebElement.
    elemento = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "select"))
    )

    # Select: classe que permite interagir com o <select> nativo.
    menu = Select(elemento)

    # .options: propriedade que devolve os elementos <option> do menu.
    # Ex.: ["Please select an option", "Option 1", "Option 2"].
    opcoes = menu.options
    assert len(opcoes) >= 3, "O menu não contém as três opções esperadas."

    for indice, opcao in enumerate(opcoes):
        # .text: texto exibido; .strip(): remove espaços externos.
        # Ex.: "  Option 2  " → "Option 2".
        logger.info("Opção %d: %s", indice, opcao.text.strip())

    # Índices começam em zero: 0=placeholder; 1=Option 1; 2=Option 2.
    # .select_by_index(2): seleciona a terceira opção pelo ÍNDICE.
    menu.select_by_index(2)

    # .first_selected_option: propriedade que devolve a opção marcada.
    # Ex.: "Option 1" → "Option 2" após selecionar o índice 2.
    selecionada = menu.first_selected_option.text.strip()
    assert selecionada == "Option 2", (
        f"Esperado 'Option 2', mas foi selecionado: {selecionada!r}"
    )
    logger.info("PARTE 1 | Aprovada: %s selecionada.", selecionada)


def clicar_botao_xpath(espera, texto):
    """Localiza e clica um botão pelo texto, usando XPath relativo."""
    # XPath relativo: //button procura botões em qualquer nível do DOM.
    # normalize-space(): compara texto ignorando espaços extras.
    # Ex.: texto="Click for JS Alert" → botão correspondente.
    xpath = f"//button[normalize-space()='{texto}']"
    botao = espera.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    botao.click()
    logger.debug("Botão acionado via XPath: %s", texto)


def parte_2_alerts(driver):
    """Trata JS Alert, JS Confirm e JS Prompt, nesta ordem."""
    logger.info("PARTE 2 | Iniciando JavaScript Alerts.")
    driver.get(URL_ALERTS)
    espera = WebDriverWait(driver, TEMPO_ESPERA)

    # 1) JS Alert: somente aceita/OK.
    clicar_botao_xpath(espera, "Click for JS Alert")
    alerta = espera.until(EC.alert_is_present())
    texto_alerta = alerta.text  # Ex.: "I am a JS Alert".
    assert texto_alerta.strip(), "O JS Alert apareceu sem mensagem."
    logger.info("JS Alert | Mensagem: %s", texto_alerta)
    alerta.accept()  # Método: equivale a clicar em OK.

    espera.until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, "#result"),
            "You successfully clicked an alert",
        )
    )
    logger.info("JS Alert | Confirmado com accept().")

    # 2) JS Confirm: clicar Cancel, não OK.
    clicar_botao_xpath(espera, "Click for JS Confirm")
    confirmacao = espera.until(EC.alert_is_present())
    logger.info("JS Confirm | Mensagem: %s", confirmacao.text)
    confirmacao.dismiss()  # Método: cancela o diálogo.

    espera.until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, "#result"), "You clicked: Cancel"
        )
    )
    resultado = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#result"))
    ).text.strip()
    assert resultado == "You clicked: Cancel", resultado
    logger.info("JS Confirm | Resultado validado: %s", resultado)

    # 3) JS Prompt: recebe um texto digitado e devolve o resultado.
    clicar_botao_xpath(espera, "Click for JS Prompt")
    prompt = espera.until(EC.alert_is_present())
    logger.info("JS Prompt | Mensagem: %s", prompt.text)

    # .send_keys(): preenche o prompt; exemplo: "" → "6326149".
    prompt.send_keys(RA)
    prompt.accept()  # Método: confirma o texto digitado.

    espera.until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#result"), RA)
    )
    resultado = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#result"))
    ).text.strip()
    assert RA in resultado, f"RA {RA} ausente de: {resultado!r}"
    logger.info("JS Prompt | RA confirmado: %s", resultado)
    logger.info("PARTE 2 | Aprovada: os três diálogos foram validados.")


def parte_3_iframes(driver):
    """Edita conteúdo no iframe e confirma retorno ao DOM principal."""
    logger.info("PARTE 3 | Iniciando iframe TinyMCE.")
    driver.get(URL_IFRAME)
    espera = WebDriverWait(driver, TEMPO_ESPERA)

    # CSS Selector: localiza um <iframe>, SEM usar o ID fixo mce_0_ifr.
    # .until(): espera o frame existir e já muda o foco para ele.
    espera.until(
        EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe")
        )
    )
    logger.info("Iframe | Foco transferido para o editor.")

    try:
        # Dentro do iframe, o editor é um elemento contenteditable.
        # Ex.: <body contenteditable="true">Texto antigo</body>.
        editor = espera.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "[contenteditable='true']")
            )
        )

        editor.clear()  # Ex.: "Your content goes here." → "".
        mensagem = f"Atividade Lab 09 - RA: {RA}"
        editor.send_keys(mensagem)  # Ex.: "" → mensagem com o RA.

        # .text: lê o conteúdo REAL digitado no editor.
        texto_editor = editor.text.strip()
        assert RA in texto_editor, (
            f"RA {RA} não foi encontrado no editor: {texto_editor!r}"
        )
        logger.info("Iframe | Texto validado: %s", texto_editor)
    finally:
        # Sempre retorna ao documento principal, mesmo se houver erro.
        driver.switch_to.default_content()
        logger.info("Iframe | Foco devolvido ao documento principal.")

    # <h3> pertence ao DOM principal, fora do editor.
    cabecalho = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "h3"))
    )
    titulo = cabecalho.text.strip()
    esperado = "An iFrame containing the TinyMCE WYSIWYG Editor"
    assert titulo == esperado, f"Cabeçalho inesperado: {titulo!r}"
    logger.info("PARTE 3 | Aprovada: retorno ao DOM principal confirmado.")


def parte_4_janelas(driver):
    """Abre, valida e fecha uma nova aba; retorna à aba original."""
    logger.info("PARTE 4 | Iniciando troca de abas/janelas.")
    driver.get(URL_WINDOWS)
    espera = WebDriverWait(driver, TEMPO_ESPERA)

    # Handle: identificador único de uma aba/janela do navegador.
    # Ex.: original="ABC123"; nova aba="DEF456" (ilustrativo).
    handle_original = driver.current_window_handle
    assert len(driver.window_handles) == 1, (
        "A Parte 4 deve começar com apenas uma janela aberta."
    )

    titulo_original = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "h3"))
    ).text.strip()
    assert titulo_original == "Opening a new window", titulo_original

    link = espera.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[normalize-space()='Click Here']")
        )
    )
    link.click()  # Ex.: 1 aba → solicitação para abrir uma 2ª aba.

    # Aguarda exatamente duas janelas; NÃO usa time.sleep().
    espera.until(EC.number_of_windows_to_be(2))
    handles = driver.window_handles  # Ex.: ["ABC123", "DEF456"].
    novos = [h for h in handles if h != handle_original]
    assert len(novos) == 1, "A nova janela não foi identificada."
    logger.info("Janelas | 2 handles identificados.")

    # .switch_to.window(): muda o foco para a nova aba.
    driver.switch_to.window(novos[0])
    try:
        cabecalho_novo = espera.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "h3"))
        )
        titulo_novo = cabecalho_novo.text.strip()
        assert titulo_novo == "New Window", (
            f"Título da nova aba diferente do esperado: {titulo_novo!r}"
        )
        logger.info("Janela nova | Conteúdo validado: %s", titulo_novo)
    finally:
        # .close(): fecha SOMENTE a aba atualmente selecionada.
        driver.close()
        # .switch_to.window(): devolve o foco à aba original.
        driver.switch_to.window(handle_original)
        logger.info("Janelas | Nova aba fechada; foco restaurado.")

    espera.until(EC.number_of_windows_to_be(1))
    assert len(driver.window_handles) == 1, (
        "Ainda existe mais de uma janela aberta."
    )
    assert driver.current_window_handle == handle_original, (
        "O foco não retornou à aba original."
    )

    titulo_retorno = espera.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "h3"))
    ).text.strip()
    assert titulo_retorno == "Opening a new window", titulo_retorno
    logger.info("PARTE 4 | Aprovada: %s.", titulo_retorno)


def bonus_fechar_janelas(driver, lista_handles, handle_original):
    """Bônus: visita e fecha N janelas novas, sempre voltando à original.

    Exemplo ilustrativo:
    lista_handles = ["ABA_ORIGINAL", "ABA_2", "ABA_3"]
    retorno = {"ABA_2": "texto da página 2", "ABA_3": "texto da 3"}
    """
    espera = WebDriverWait(driver, TEMPO_ESPERA)
    conteudos = {}

    try:
        for handle in lista_handles:
            if handle == handle_original:
                continue  # Não fecha a aba original.

            driver.switch_to.window(handle)
            try:
                # O body permite ler o conteúdo mesmo em outras páginas.
                corpo = espera.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "body"))
                )
                texto = corpo.text.strip()
                assert texto, "A janela nova não apresentou texto."
                conteudos[handle] = texto
                logger.info("BÔNUS | Janela %s: %.120s", handle, texto)
            finally:
                driver.close()  # Encerra a janela que acabou de examinar.
    finally:
        # Retorna mesmo que alguma janela cause uma exceção.
        driver.switch_to.window(handle_original)

    assert len(driver.window_handles) == 1, (
        "O bônus deveria deixar aberta apenas a janela original."
    )
    assert driver.current_window_handle == handle_original
    return conteudos


def executar_automacao():
    """Coordena as quatro partes e encerra o WebDriver obrigatoriamente."""
    configurar_logs()
    driver = None

    try:
        # WebDriver: classe que inicia e controla o Chrome.
        driver = webdriver.Chrome()
        logger.info("Lab 09 | Navegador iniciado. RA=%s", RA)

        parte_1_selects(driver)
        parte_2_alerts(driver)
        parte_3_iframes(driver)
        parte_4_janelas(driver)

        logger.info("LAB 09 | SUCESSO: quatro partes concluídas.")
    except (TimeoutException, WebDriverException, AssertionError):
        # .exception(): salva mensagem e traceback no terminal e no .log.
        logger.exception("LAB 09 | Falha na execução ou validação.")
        raise  # Mantém o erro visível; não anuncia sucesso indevidamente.
    finally:
        if driver is not None:
            # .quit(): encerra todas as janelas e a sessão do WebDriver.
            driver.quit()
            logger.info("Lab 09 | Sessão do navegador encerrada.")


if __name__ == "__main__":
    executar_automacao()
