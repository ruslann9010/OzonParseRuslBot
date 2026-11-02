import json
import redis.asyncio as aioredis
from config import Config

class RedisQueueManager:


    def __init__(self, queue_name: str = "ozon_products") -> None:
        self.host = Config.REDIS_HOST
        self.port = Config.REDIS_PORT
        self.queue_name = queue_name
        self.redis = None

    async def connect(self):
        """Устанавливает соединение с сервером Redis."""
        if not self.redis:
            self.redis = aioredis.Redis(
                host=self.host, 
                port=self.port, 
                decode_responses=True,
                health_check_interval=0)     


    async def push_product(self, product_data: dict):
        """Отправляет спарсенный товар в хвост очереди Redis."""
        await self.connect()
        json_data = json.dumps(product_data)
        assert self.redis is not None 
        await self.redis.rpush(self.queue_name, json_data) # type: ignore

    async def pop_product(self):
        """Извлекает один товар из головы очереди. Если очередь пуста, блокирует выполнение."""
        await self.connect()
        assert self.redis is not None
        
        result = await self.redis.blpop(self.queue_name, timeout=0) # type: ignore
        if result:
            data_string = result[1] if isinstance(result, (list, tuple)) else result
            return json.loads(data_string)
        return None


    async def close(self):
        """Закрывает соединение с Redis."""
        if self.redis:
            await self.redis.close()
        