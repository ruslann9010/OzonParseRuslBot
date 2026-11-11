"""Browser lifecycle and context management utilities built on Playwright."""

from playwright.async_api import async_playwright, Browser, BrowserContext

from config import Config


class BrowserManager:
    """Manages an asynchronous Playwright Chromium browser instance and contexts.

    Encapsulates lazy browser initialization with anti-detection launch flags,
    optional proxy routing, isolated browser context creation, and graceful
    resource cleanup.

    Attributes:
        _playwright (Playwright | None): Underlying Playwright controller instance.
        _browser (Browser | None): Active Chromium browser instance.
    """
    def __init__(self) -> None:
        """Initializes the BrowserManager with uninitialized Playwright and browser."""
        self._playwrite = None
        self._browser = None


    async def get_browser(self) -> Browser:
        """Lazily launches and returns a configured Chromium browser instance.

        If a browser instance is not yet active, starts Playwright and launches
        Chromium with automation-masking flags and optional proxy settings
        defined in ``Config``.

        Returns:
            An active Playwright ``Browser`` instance.

        Raises:
            AssertionError: If Playwright fails to start or the browser fails to launch.
        """
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
        """Creates a new isolated browser context with custom user-agent and viewport.

        Returns:
            A configured Playwright ``BrowserContext`` ready for page creation.
        """
        browser = await self.get_browser()
        context = await browser.new_context(
            user_agent=Config.USER_AGENT, # type: ignore
            viewport=Config.VIEWPORT)     # type: ignore
        return context
             

    async def close(self):
        """Closes the active browser instance and stops the Playwright engine."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        
