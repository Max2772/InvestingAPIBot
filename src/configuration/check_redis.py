from aiogram.fsm.storage.redis import RedisStorage


async def check_redis(storage: RedisStorage) -> bool:
    await storage.redis.set(name='1', value='hello', ex=100)
    return await storage.redis.get(name='1') == b'hello'