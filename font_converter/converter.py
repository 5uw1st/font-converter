#!usr/bin/env python3
# -*- coding:utf-8 _*-

import logging
import re
from base64 import b64decode, b64encode
from io import BytesIO

import pytesseract
import requests
from PIL import Image, ImageFont, ImageDraw, ImageColor

from .helper import RedisClient, HEADERS


class FontConverter(object):
    """
    Font converter
    """

    def __init__(self, font_url, logger=None, redis_client=None, debug=False, lang="chi_sim", pool_size=5, **kwargs):
        self._font_url = font_url
        self._debug = debug
        self._lang = lang
        self._pool_size = pool_size
        self.logger = logger or logging.getLogger()
        self._reg_font_sign = re.compile(r'fonts-styles/fonts/\w+/(\w+?)/tyc-num')
        self._expire_time = kwargs.get("expire_time") or 30 * 24 * 3600
        self._redis_client = redis_client or RedisClient(**kwargs)
        self._font_content = None
        self._font_key = ""
        self._word_key = ""
        self._words_dict = {}
        self._init_data()

    def _init_data(self):
        sign = self._get_font_sign(font_url=self._font_url)
        self._font_key = self._get_redis_key(sign=sign, key_type="CONTENT")  # init key
        self._word_key = self._get_redis_key(sign=sign, key_type="WORD")
        self._font_content = self._get_font_content()
        self.logger.debug("===>Init data, sign:{1}, font_url:{0}".format(self._font_url, sign))

    def _get_redis_key(self, sign, key_type="CONTENT"):
        """
        获取redis key, eg: FontConverter:CONTENT:5534d7da
        :param sign: str font sign
        :param key_type: str CONTENT/MAP
        :return: str
        """
        return ":".join([self.__class__.__name__, key_type, sign])

    def _download_font(self, font_url):
        """
        获取字体内容
        :param font_url: str
        :return: font_bytes
        """
        return requests.get(font_url, headers=HEADERS, timeout=10).content

    def _get_font_sign(self, font_url):
        """
        获取字体签名(用于判断是否更新)
        :param font_url: str
        :return: str
        """
        _ret = self._reg_font_sign.search(font_url)
        if not _ret:
            raise RuntimeError("font url validate:{0}".format(font_url))
        return _ret.group(1)

    def _get_font_content(self):
        """
        获取字体文件内容
        :return: bytes
        """
        b64_value = self._redis_client.get(self._font_key)
        if b64_value:
            content = b64decode(b64_value.decode())
        else:
            content = self._download_font(font_url=self._font_url)
            self._save_font_to_redis(key=self._font_key, font_bytes=content)
        return content

    def _save_font_to_redis(self, key, font_bytes):
        """
        保存字体内容
        :param key: str
        :param font_bytes: bytes
        :return: bool
        """
        b64 = b64encode(font_bytes)
        return self._redis_client.setex(key, self._expire_time, b64)

    def _parse_word_from_font(self, word):
        img = Image.new("RGB", (300, 300), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(BytesIO(self._font_content), 200)
        draw.text((10, 10), text=word, font=font, fill=ImageColor.getcolor('black', 'RGB'))
        if self._debug:
            img.show()
        if word.isdigit():
            ps = "--psm 6 digits"
        else:
            ps = "--psm 8 -l {0}".format(self._lang)
        result = pytesseract.image_to_string(img, config=ps)
        if result == "":
            return word
        else:
            return result[0]

    def _get_origin_word(self, now_word):
        """
        获取原始word
        :param now_word: str
        :return: dict
        """
        origin = self._redis_client.hget(self._word_key, now_word)
        if origin is not None:
            return origin.decode()
        # not existed, need parse
        origin_word = self._parse_word_from_font(word=str(now_word))
        self._save_word_to_redis(now_word=now_word, origin_word=origin_word)
        self.logger.info("===>New word, [{0}]==>[{1}]".format(now_word, origin_word))
        return origin_word

    def _save_word_to_redis(self, now_word, origin_word):
        """
        保存word映射关系
        :param now_word: str
        :param origin_word: str
        :return: bool
        """
        self._redis_client.hsetnx(self._word_key, now_word, origin_word)
        if self._redis_client.ttl(self._word_key) < 0:
            self._redis_client.expire(self._word_key, self._expire_time)

    def _do_convert(self, word):
        """
        开始转换
        :param word:
        :return:
        """
        if word in self._words_dict.keys():
            return self._words_dict[word]
        origin = self._get_origin_word(now_word=word)
        self._words_dict[word] = origin
        return origin

    def get_dict(self):
        return self._words_dict

    def clear(self):
        self._redis_client.delete(self._word_key)
        self._redis_client.delete(self._font_content)
        del self._words_dict

    def convert(self, words):
        """
        转换字体
        :return: str
        """
        result = []
        for word in words:
            # TODO use process pool
            result.append(self._do_convert(word=word))
        return "".join(result)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __str__(self):
        return "<{0}|{1}>".format(self.__class__.__name__, self._font_url)
