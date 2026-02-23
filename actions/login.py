import os
from playwright.sync_api import Page
from core.logger import setup_logger

logger = setup_logger()


def login(page: Page) -> bool:
    """
    Realiza o login em tasker.somosocta.com.

    Args:
        page: Instância da página do Playwright.

    Returns:
        True se o login foi bem-sucedido, False caso contrário.
    """
    login_url = os.getenv("LOGIN_URL")
    username = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    if not username or not password:
        raise ValueError("Variáveis EMAIL e PASSWORD não definidas no .env")

    logger.info(f"Acessando página de login: {login_url}")
    page.goto(login_url)
    page.wait_for_load_state("networkidle")

    page.fill("input[type='email']", username)
    page.fill("input[type='password']", password)

    # Dispara o click e aguarda a navegação resultante juntos
    with page.expect_navigation(timeout=20000):
        page.click("button[type='submit']")

    page.wait_for_load_state("networkidle", timeout=20000)

    current_url = page.url
    logger.info(f"URL após submit: {current_url}")

    # Falhou se ainda estiver na página de login
    if "/login" in current_url:
        logger.error("Falha no login — ainda na página de login. Verifique as credenciais.")
        return False

    logger.info("Login realizado com sucesso.")
    return True
