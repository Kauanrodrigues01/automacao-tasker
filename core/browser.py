import os
from playwright.sync_api import sync_playwright, Browser, Page


class BrowserSession:
    """Gerencia a sessão do browser com Playwright."""

    def __init__(self):
        self._playwright = None
        self._browser: Browser = None
        self._page: Page = None

    def start(self) -> Page:
        """Inicia o browser e retorna a página ativa."""
        headless = os.getenv("HEADLESS", "true").lower() == "true"

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=headless)
        self._page = self._browser.new_page()

        return self._page

    def stop(self):
        """Fecha o browser e encerra o Playwright."""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

        self._page = None
        self._browser = None
        self._playwright = None

    def __enter__(self) -> Page:
        return self.start()

    def __exit__(self, *args):
        self.stop()
