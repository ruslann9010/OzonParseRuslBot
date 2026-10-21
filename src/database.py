import re
import aiosqlite
from datetime import datetime


class DataBaseDb:
    """ Database client layer for managing product data persistence.
    
    This class handles asynchronous interactions with the local SQLite database,
    including table initialization, product recording, and price update logic.
    """

    @staticmethod
    async def init_db():
        """Initializes the database by creating the required tables if they do not exist.
        
        Creates the 'products' table with a schema tailored for storing scraped
        enforcing constraints like a unique product ID and URL.
        """
        async with aiosqlite.connect("database.db") as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT UNIQUE,
                    title TEXT,
                    price INTEGER,
                    url TEXT UNIQUE,
                    updated_at TIMESTAMP)""")
            await db.commit()


    @staticmethod
    async def save_or_update_product(product_data: dict):
        """Saves a new product to the database or updates its price if it already exists.
        
        This method parses raw product attributes (cleaning the price string into 
        an integer and extracting a unique product ID from the URL), then
        executes an UPSERT (INSERT ON CONFLICT) statement.

        Args:
            product_data (dict): A dictionary containing raw scraped item data.
                Expected keys: 'title' (str), 'price' (str), and 'url' (str).
        """
        price = product_data.get('price', '0')
        clean_price = int(re.sub(r'[^\d]', '', price)) if price else 0
        url =  product_data.get('url', '')
        product_id_match = re.search(r'/product/[^/]*?-?(\d+)', url)
        product_id = product_id_match.group(1) if product_id_match else None
        if not product_id:
            product_id = url.split('/')[-2] if '/' in url else url
        current_time = datetime.now().isoformat()
        async with aiosqlite.connect("database.db") as db:
            await db.execute("""
                INSERT INTO products (product_id, title, price, url, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(product_id) DO UPDATE SET
                    price = excluded.price,
                    updated_at = excluded.updated_at
            """, (product_id, product_data['title'], clean_price, url, current_time))
            await db.commit()
