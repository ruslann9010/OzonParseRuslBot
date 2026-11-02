import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MAX_RETRIES = 3
    REDIS_PORT = 6379
    PAGE_TIMEOUT = 30000
    REDIS_HOST = "localhost"
    DEFAULT_SEARCH_QUERY = "ноутбук"
    HEADLESS = os.getenv("HEADLESS", "False").lower() in ("true", "1", "yes")
    PROXY_SERVER = os.getenv("PROXY_SERVER", None)
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    VIEWPORT = {"width": 1920, "height": 1080}  
