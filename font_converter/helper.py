#!usr/bin/env python3
# -*- coding:utf-8 _*-

import os

import redis

HEADERS = {
    "Sec-Fetch-Mode": "cors",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
}


class RedisClient(object):
    """
    Redis connect client
    """

    def __init__(self, redis_uri=None, **kwargs):
        self.__conn = None
        self.redis_uri = redis_uri or kwargs.get("redis_uri")
        if not self.redis_uri:
            raise RuntimeError("Must set redis_uri")

    def _get_conn(self):
        if not self.__conn:
            self.__conn = redis.from_url(url=self.redis_uri)
        return self.__conn

    @property
    def conn(self):
        return self._get_conn()

    def __getattr__(self, item):
        return getattr(self.conn, item)

    def test(self):
        return self.ping()


def get_env(key, default=None):
    return os.environ.get(key, default=default)
