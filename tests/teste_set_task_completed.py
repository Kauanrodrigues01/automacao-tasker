import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from core.browser import BrowserSession
from actions.login import login
from actions.set_task_completed import set_task_completed

load_dotenv()

TASK_ID = "NEO-168"  # Altere para o ID da task que deseja testar


def main():
    print(f"Iniciando teste: set_task_completed ({TASK_ID})...")

    with BrowserSession() as page:
        sucesso_login = login(page)
        if not sucesso_login:
            print("Login FALHOU — abortando teste.")
            return

        sucesso = set_task_completed(page, TASK_ID)

        if sucesso:
            print(f"Task {TASK_ID} marcada como Concluída com sucesso.")
        else:
            print(f"FALHOU ao marcar task {TASK_ID} como Concluída.")

        input("Pressione Enter para fechar o browser...")


if __name__ == "__main__":
    main()
