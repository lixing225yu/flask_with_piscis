from typing import Mapping
from piscis.core.wrappers import Singleton
from piscis.cache.base_cache import BaseCache
from rediscluster import RedisCluster
from inspect import getfullargspec
import pickle
import hashlib
import functools
from piscis.utils.timeutil import to_local
from piscis.cache.redlock import RedLock
import time
from contextlib import contextmanager
from piscis.config.global_config import global_config


def wrap_key(k='key'):
    """
    给redis缓存key包装前缀
    :param k: 缓存键的参数名称
    :return:
    """

    def wrapper(func):
        @functools.wraps(func)
        def deco(*args, **kwargs):
            # 目前只支持*args
            argspec = getfullargspec(func)
            if k in argspec.args:
                i = argspec.args.index(k)
                if i >= 0:
                    if isinstance(args[i], list):
                        for j in range(len(args[i])):
                            args[i][j] = RedisCache.key_prefix + args[i][j]
                    else:
                        args = list(args)
                        args[i] = RedisCache.key_prefix + args[i]
                        args = tuple(args)
            return func(*args, **kwargs)

        return deco

    return wrapper


@Singleton
class RedisCache(BaseCache):
    key_prefix = ''

    def __init__(self,
                 server_nodes,
                 key_prefix,
                 socket_connect_timeout=10,
                 socket_timeout=3,
                 password=None):
        if password:
            self._redis = RedisCluster(
                startup_nodes=server_nodes,
                socket_connect_timeout=socket_connect_timeout,
                socket_timeout=socket_timeout,
                password=password,
            )
        else:
            self._redis = RedisCluster(
                startup_nodes=server_nodes,
                socket_connect_timeout=socket_connect_timeout,
                socket_timeout=socket_timeout
            )

        RedisCache.key_prefix = key_prefix

    def ensure_client(self):
        if not self._redis:
            raise Exception('redis_client is None')

    @classmethod
    def __make_cache_key(cls, func, func_args, func_kwargs, key=None):
        """ :return cache key """
        if key:
            return '%s' % (key)

        new_args = []
        arg_num = 0
        argspec = getfullargspec(func)

        args_len = len(argspec.args)
        for i in range(args_len):
            if i == 0 and argspec.args[i] in ['self', 'cls']:
                arg_num += 1
                try:
                    arg = pickle.dumps(func_args[0])
                except Exception as e:
                    # print e
                    arg = None
            elif argspec.args[i] in func_kwargs:
                arg = func_kwargs[argspec.args[i]]
            elif arg_num < len(func_args):
                arg = func_args[arg_num]
                arg_num += 1
            elif abs(i - args_len) <= len(argspec.defaults):
                arg = argspec.defaults[i - args_len]
                arg_num += 1
            else:
                arg = None
                arg_num += 1
            if arg and not cls._check_value(arg):
                arg = pickle.dumps(arg)

            new_args.append(arg)
        args_key = hashlib.md5()
        args_key.update(('%s' % new_args).encode('utf-8'))
        # args_key = base64.b64encode(args_key.digest())[:16]
        args_key = args_key.hexdigest()
        return '%s:%s' % (func.__name__, args_key)

    def cache(self, timeout=None, key=None):
        """decorator，返回使用缓存的方法"""

        def decorator(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                cache_key = self.__make_cache_key(f, args, kwargs, key)
                v = self.get(cache_key)
                if v:
                    return pickle.loads(v)
                v = f(*args, **kwargs)
                if v is not None:
                    if timeout:
                        self.setex(cache_key, pickle.dumps(v), timeout)
                    else:
                        self.set(cache_key, pickle.dumps(v))
                    self._redis.sadd(
                        f"{RedisCache.key_prefix}cache_deco:{f.__name__}_keys",
                        cache_key)
                return v

            return decorated_function

        return decorator

    def remove_deco_cache(self, func_name):
        key = f"{self.key_prefix}cache_deco:{func_name}_keys"
        keys = [str(k, encoding='utf-8') for k in self._redis.smembers(key)]
        self.delete(keys)
        self._redis.delete(key)

    @wrap_key()
    def set(self, key, value, **kwargs):
        self.ensure_client()
        return self._redis.set(key, value, **kwargs)

    def setex(self, name, value, ex):
        return self.set(name, value, ex=ex)

    @wrap_key()
    def setnx(self, key, value):
        self.ensure_client()
        return self._redis.setnx(key, value)

    @wrap_key()
    def get(self, key):
        self.ensure_client()
        return self._redis.get(key)

    @wrap_key()
    def delete(self, key):
        self.ensure_client()
        if not isinstance(key, list):
            key = [key]
        return self._redis.delete(*key)

    # 注意，如果键的数量很多，将会很慢，相对于keys，不会太影响性能
    @wrap_key('pattern')
    def clear(self, pattern="*"):
        for key in self._redis.keys(pattern):
            self._redis.delete(key)

    @wrap_key()
    def expire_at(self, key, when):
        """指定过期时间"""
        self.ensure_client()
        self._redis.expireat(key, to_local(when))

    @wrap_key()
    def expire(self, key, time):
        self.ensure_client()
        self._redis.expire(key, time)

    @wrap_key()
    def incr(self, key, amount=1):
        """incr"""
        self.ensure_client()
        return self._redis.incr(key, amount)

    @wrap_key('keys')
    def mget(self, keys):
        self.ensure_client()
        return self._redis.mget(keys)

    @wrap_key()
    def hmset(self, key, value):
        self.ensure_client()
        return self._redis.hmset(key, value)

    @wrap_key()
    def hgetall(self, key):
        self.ensure_client()
        return self._redis.hgetall(key)

    @wrap_key()
    def hdel(self, key, field):
        self.ensure_client()
        if not isinstance(field, list):
            field = [field]
        return self._redis.hdel(key, *field)

    @wrap_key()
    def setbit(self, key, offset, value):
        self.ensure_client()
        return self._redis.setbit(key, offset, value)

    @wrap_key()
    def getbit(self, key, offset):
        self.ensure_client()
        return self._redis.getbit(key, offset)

    @wrap_key()
    def get_key_create_time(self, key, timeout):
        ttl = self._redis.ttl(key)
        creatime_stamp = int(time.time()) + ttl - timeout
        return creatime_stamp

    @contextmanager
    @wrap_key()
    def locked(self, key, **kwargs):
        lock = RedLock(key, connection_details=[self._redis], **kwargs)
        yield lock.acquire()
        lock.release()


redis_cli = RedisCache(global_config.settings.redis.servers,
                       global_config.settings.redis.prefix, password=global_config.settings.redis.password)
