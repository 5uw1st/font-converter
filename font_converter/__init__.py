#!usr/bin/env python3
# -*- coding:utf-8 _*-

import pytesseract

from .converter import FontConverter
from .helper import get_env, RedisClient

__all__ = ["FontConverter", "RedisClient", "set_tesseract_path"]


def set_tesseract_path():
    tesseract_path = get_env(key="TESSERACT_PATH")
    if not tesseract_path:
        raise RuntimeError("Must set TESSERACT_PATH in system path")
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


set_tesseract_path()
