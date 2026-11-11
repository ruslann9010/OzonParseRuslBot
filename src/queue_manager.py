import json
import redis.asyncio as aioredis
from config import Config

class RedisQueueManager:
    """Manages asynchronous Redis queues for scraped products and search tasks.

        This class handles connection lifecycle, serialization, and FIFO queue
        operations using Redis lists to decouple the Telegram bot, scraper worker,
        and database consumer.

        Attributes:
            host (str): Redis server hostname or IP address.
            port (int): Redis server port number.
            queue_name (str): Name of the Redis list storing scraped product data.
            tasks_queue (str): Name of the Redis list storing incoming search tasks.
            redis (aioredis.Redis | None): Active asynchronous Redis client instance.
        """

    def __init__(
            self, 
            queue_name: str = "ozon_products", 
            tasks_queue: str = "ozon_search_tasks"
            ) -> None:
        """Initializes the RedisQueueManager with connection and queue settings.

        Args:
            queue_name: Name of the queue used for scraped product items.
                Defaults to "ozon_products".
            tasks_queue: Name of the queue used for user search requests.
                Defaults to "ozon_search_tasks".
        """
        self.host = Config.REDIS_HOST
        self.port = Config.REDIS_PORT
        self.queue_name = queue_name
        self.tasks_queue = tasks_queue
        self.redis = None

    async def connect(self):
        """Establishes an asynchronous connection to the Redis server.

        If a connection is already active, this method does nothing.
        """
        if not self.redis:
            self.redis = aioredis.Redis(
                host=self.host, 
                port=self.port, 
                decode_responses=True,
                health_check_interval=0)     


    async def push_product(self, product_data: dict):
        """Serializes and pushes a scraped product item to the tail of the product queue.

        Args:
            product_data: Dictionary containing parsed product details (e.g.,
                title, price, url).
        """
        await self.connect()
        json_data = json.dumps(product_data)
        assert self.redis is not None 
        await self.redis.rpush(self.queue_name, json_data) # type: ignore


    async def pop_product(self) -> dict[str, Any] | None:
        """Blocks until a product item is available at the head of the queue and pops it.

        Returns:
            A dictionary representing the parsed product data, or None if the
            operation was interrupted or returned an empty result.
        """
        await self.connect()
        assert self.redis is not None
        result = await self.redis.blpop(self.queue_name, timeout=0) # type: ignore
        if result:
            data_string = result[1] if isinstance(result, (list, tuple)) else result
            return json.loads(data_string)
        return None


    async def push_search_task_queue(self, chat_id: int, query: str) -> None:
        """Enqueues a new search task requested by a user into the tasks queue.

        Args:
            chat_id: Telegram chat identifier of the user who initiated the search.
            query: Search phrase or product name to be scraped on Ozon.
        """
        if not self.redis:
            await self.connect()
        task_data = {"chat_id": chat_id, "query": query}
        payload = json.dumps(task_data, ensure_ascii=False)
        await self.redis.rpush(self.tasks_queue, payload) #type: ignore


    async def get_search_task(self) -> None:
        """Blocks until a search task arrives in the tasks queue and retrieves it.

        Returns:
            A dictionary containing 'chat_id' and 'query' keys, or None if no
            task was retrieved.
        """
        if not self.redis:
            await self.connect()
        result = await self.redis.blpop([self.tasks_queue], timeout=0) #type: ignore
        if result is not None:
            _, payload = result
            return json.loads(payload)
        return None


    async def close(self):
        """Gracefully closes the active Redis connection if it exists."""
        if self.redis:
            await self.redis.close()
            self.redis = None
        