from playwright.async_api import async_playwright, Browser, BrowserContext

from config import Config


class BrowserManager:

    def __init__(self) -> None:
        self._playwrite = None
        self._browser = None


    async def get_browser(self) -> Browser:

        if self._browser is None:  
            self._playwright = await async_playwright().start() 
            launch_args = ["--disable-blink-features=AutomationControlled"]
            proxy_config = {"server": Config.PROXY_SERVER} if Config.PROXY_SERVER else None
            assert self._playwright is not None, "Playwright core failed to start"     
            self._browser = await self._playwright.chromium.launch(headless=False,
                                args=launch_args, proxy=proxy_config)  # type: ignore             
        assert self._browser is not None, "Browser launch failed"
        return self._browser


    async def create_context(self) -> BrowserContext:

        browser = await self.get_browser()
        context = await browser.new_context(
            user_agent=Config.USER_AGENT, # type: ignore
            viewport=Config.VIEWPORT)     # type: ignore
        return context
             

    async def close(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        
