import os
from playwright.sync_api import Page
from core.logger import setup_logger

logger = setup_logger()


def set_task_executing(page: Page, task_id: str) -> bool:
    """
    Marca uma task como "Em execução" clicando no botão "Iniciar tarefa".

    Args:
        page: Instância da página do Playwright.
        task_id: ID da task (ex: NEO-168).

    Returns:
        True se o status foi alterado com sucesso, False caso contrário.
    """
    issues_url = os.getenv("ISSUES_URL")
    search_placeholder = os.getenv("SEARCH_PLACEHOLDER")
    btn_iniciar = os.getenv("BTN_INICIAR_TAREFA")

    logger.info(f"Buscando task {task_id} para iniciar execução...")
    logger.info(f"URL destino: {issues_url}")

    page.goto(issues_url)
    page.wait_for_load_state("networkidle")
    logger.info(f"Página carregada. URL atual: {page.url}")

    search_input = page.locator(f"input[placeholder='{search_placeholder}']")
    search_input.fill(task_id)
    # Aguarda debounce do filtro e atualização da tabela (pode ser filtro local, sem request HTTP)
    page.wait_for_timeout(1500)
    page.wait_for_load_state("networkidle")

    rows = page.locator("tbody tr")
    count = rows.count()
    logger.info(f"Linhas encontradas na tabela após busca por '{task_id}': {count}")

    if count == 0:
        logger.error(f"Task {task_id} não encontrada na listagem.")
        return False

    if count > 1:
        logger.error(f"Busca por '{task_id}' retornou {count} resultados. Esperado: 1.")
        return False

    start_button = rows.first.locator(f"button[title='{btn_iniciar}']")

    if not start_button.is_visible():
        logger.warning(f"Botão '{btn_iniciar}' não encontrado para task {task_id} — task já está em execução ou status não permite.")
        return False

    # Monitora respostas de rede geradas pelo clique
    network_responses: list[str] = []

    def _on_response(response):
        method = response.request.method
        if method in ("POST", "PUT", "PATCH", "DELETE"):
            network_responses.append(f"{response.status} {method} {response.url}")

    page.on("response", _on_response)

    start_button.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    page.remove_listener("response", _on_response)

    if network_responses:
        logger.info(f"Requisições após clique em '{btn_iniciar}':")
        for r in network_responses:
            logger.info(f"  → {r}")
    else:
        logger.warning(f"Nenhuma requisição POST/PUT/PATCH/DELETE detectada após clicar em '{btn_iniciar}'.")

    logger.info(f"Task {task_id} marcada como Em execução.")
    return True
