import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from core.browser import BrowserSession
from actions.login import login
from actions.add_hours import add_hours

load_dotenv()

TASK_ID = "NEO-108"  # Altere para o ID da task que deseja testar
HOURS = 4            # Quantidade de horas a registrar (aceita decimais: 8.5 = 8h30m)


def main():
    print(f"Iniciando teste: add_hours ({TASK_ID}, {HOURS}h)...")

    with BrowserSession() as page:
        sucesso_login = login(page)
        if not sucesso_login:
            print("Login FALHOU — abortando teste.")
            return

        sucesso = add_hours(page, TASK_ID, HOURS)

        if sucesso:
            print(f"Horas registradas na task {TASK_ID} com sucesso.")
        else:
            print(f"FALHOU ao registrar horas na task {TASK_ID}.")

        input("Pressione Enter para fechar o browser...")


if __name__ == "__main__":
    main()
