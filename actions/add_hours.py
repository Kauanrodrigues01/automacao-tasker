import os
from playwright.sync_api import Page
from core.logger import setup_logger

logger = setup_logger()


def _format_hours(hours: float) -> str:
    """Converte horas decimais para o formato aceito pelo campo (ex: 8h, 8h30m)."""
    h = int(hours)
    m = int(round((hours - h) * 60))
    if m == 0:
        return f"{h}h"
    return f"{h}h{m:02d}m"


def add_hours(page: Page, task_id: str, hours: float, description: str = "") -> bool:
    """
    Registra horas em uma task via modal "New Time Entry".

    Args:
        page: Instância da página do Playwright.
        task_id: ID da task (ex: NEO-168).
        hours: Quantidade de horas a registrar (ex: 8 ou 8.5).
        description: Não utilizado pelo modal atual (campo não existe).

    Returns:
        True se o registro foi salvo com sucesso, False caso contrário.
    """
    issues_url = os.getenv("ISSUES_URL")
    search_placeholder = os.getenv("SEARCH_PLACEHOLDER")
    btn_lancar = os.getenv("BTN_LANCAR_HORAS")
    btn_save = os.getenv("BTN_SAVE")

    hours_str = _format_hours(hours)
    logger.info(f"Registrando {hours_str} na task {task_id}...")

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

    launch_button = rows.first.locator(f"button[title='{btn_lancar}']")
    launch_button.click()

    modal = page.locator("div[role='dialog'][data-state='open']")
    modal.wait_for(state="visible", timeout=10000)

    hours_input = modal.locator("input#horas")
    hours_input.clear()
    hours_input.fill(hours_str)

    modal.locator("button", has_text=btn_save).click()
    page.wait_for_load_state("networkidle")

    logger.info(f"{hours_str} registradas na task {task_id} com sucesso.")
    return True
