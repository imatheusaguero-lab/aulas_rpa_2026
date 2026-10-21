
import time
import pyautogui

# Configurações de segurança
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

# Abre a pesquisa do Windows
pyautogui.press("win")

# Pesquisa o Bloco de Notas
pyautogui.write("notepad", interval=0.1)
pyautogui.press("enter")

# Aguarda o aplicativo abrir
time.sleep(2)

# Texto do relatório
texto = "Relatório de Execução Automática - RPA PyAutoGUI Ativo!"

# Digita o texto de forma visível, com suporte a acentos
pyautogui.write("Relat", interval=0.1)
pyautogui.hotkey("ctrl", "a")
pyautogui.write("")

# Insere o texto Unicode por meio da área de transferência
import subprocess

subprocess.run(
    ["clip"],
    input=texto.encode("utf-16le"),
    check=True
)
pyautogui.hotkey("ctrl", "v")

# Abre a janela para salvar
pyautogui.hotkey("ctrl", "s")
time.sleep(1)

# Define o nome do arquivo
pyautogui.write("status_bot.txt", interval=0.1)
pyautogui.press("enter")
