import os
from dotenv import load_dotenv

load_dotenv()


HEADLESS = os.getenv("HEADLESS", "False").lower() in ("true", "1", "yes")
PROXY_SERVER = os.getenv("PROXY_SERVER", None)
