import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from core.browser import BrowserSession
from actions.login import login

load_dotenv()


def main():
    print("Iniciando teste de login...")

    with BrowserSession() as page:
        sucesso = login(page)

        if sucesso:
            print("Login OK — pressione Enter para fechar o browser.")
        else:
            print("Login FALHOU — verifique as credenciais no .env.")

        input()


if __name__ == "__main__":
    main()
