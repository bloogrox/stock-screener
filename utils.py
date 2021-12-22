import json
from abc import ABC, abstractmethod
from redis import Redis


class BaseStorage(ABC):
    @abstractmethod
    def get(self, key) -> str:  # noqa
        pass  # noqa

    @abstractmethod
    def set(self, key: str, value: str, ttl: int) -> None:
        pass


class RedisStorage(BaseStorage):
    def __init__(self, uri):
        self.conn = Redis.from_url(uri)

    def get(self, key) -> str:  # noqa
        return self.conn.get(key)  # noqa

    def set(self, key: str, value: str, ttl: int) -> None:
        self.conn.set(key, value, ex=ttl)


def cache(storage: BaseStorage, key: str, ttl: int):
    def decorator(function):
        def wrapper(*args, **kwargs):
            res = storage.get(key)
            if res:
                return json.loads(res)
            else:
                data = function(*args, **kwargs)
                storage.set(key, json.dumps(data), ttl=ttl)
                return data
        return wrapper
    return decorator


# def cache(uri, key: str):
#     def decorator(function):
#         def wrapper(*args, **kwargs):
#             r = Redis.from_url(uri)
#             res = r.get(key)
#             if res:
#                 return json.loads(res)
#             else:
#                 data = function(*args, **kwargs)
#                 r.set(key, json.dumps(data), ex=86400)
#                 return data
#         return wrapper
#     return decorator
