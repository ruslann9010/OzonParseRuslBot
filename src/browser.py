import logging

from playwright.async_api import async_playwright, Browser, BrowserContext, Page 
from config import HEADLESS, PROXY_SERVER
from typing import Optional, Any


logger = logging.getLogger(__name__)


class OzBrowserClient:

    def __init__(self) -> None:
        """ Инициализация внутренних полей класса.
        Здесь вы просто объявляете переменные, которые изначально равны None,
        чтобы затем сохранить в них запущенные процессы браузера.
        """
        self._playwright: Optional[Any] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None


    async def init_browser(self) -> Page:
        """ Launches the browser instance, configures anti-detection headers,

        and creates a fresh viewport page.  
        :return: An active asynchronous Playwright Page object.
        """
        logger.info("Initializing Playwright browser client...")
        self._playwright = await async_playwright().start() 
        launch_args = ["--disable-blink-features=AutomationControlled"]
        proxy_config = {"server": PROXY_SERVER} if PROXY_SERVER else None
        assert self._playwright is not None, "Playwright core failed to start"

        self.browser = await self._playwright.chromium.launch(
            headless=HEADLESS,
            args=launch_args,
            proxy=proxy_config # type: ignore
        )
        
        assert self.browser is not None, "Browser launch failed"
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080})
        
        page = await self.context.new_page()
        return page 


    async def close_browser(self) -> None:
        """ Gracefully closes context, browser process, and stops the main Playwright loop.
        This method prevents memory leaks and stale system processes.
        """
        logger.info("Closing browser sessions...")
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()
