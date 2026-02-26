import os
from playwright.sync_api import Page
from core.logger import setup_logger

logger = setup_logger()


def set_task_completed(page: Page, task_id: str) -> bool:
    """
    Marca uma task como "Concluída" via dropdown de status.

    Args:
        page: Instância da página do Playwright.
        task_id: ID da task (ex: NEO-168).

    Returns:
        True se o status foi alterado com sucesso, False caso contrário.
    """
    issues_url = os.getenv("ISSUES_URL")
    search_placeholder = os.getenv("SEARCH_PLACEHOLDER")
    status_concluida = os.getenv("STATUS_CONCLUIDA")

    logger.info(f"Alterando task {task_id} para status: Concluída...")

    page.goto(issues_url)
    page.wait_for_load_state("networkidle")

    search_input = page.locator(f"input[placeholder='{search_placeholder}']")
    search_input.fill(task_id)
    page.wait_for_timeout(1500)
    page.wait_for_load_state("networkidle")

    rows = page.locator("tbody tr")
    count = rows.count()

    if count == 0:
        logger.error(f"Task {task_id} não encontrada na listagem.")
        return False

    if count > 1:
        logger.error(f"Busca por '{task_id}' retornou {count} resultados. Esperado: 1.")
        return False

    status_button = rows.first.locator("button[role='combobox']").first
    status_button.click()

    option = page.locator("[role='option']", has_text=status_concluida)
    option.wait_for(state="visible", timeout=10000)
    option.click()

    page.wait_for_load_state("networkidle")

    logger.info(f"Task {task_id} marcada como Concluída.")
    return True
