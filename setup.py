#!usr/bin/env python3
# -*- coding:utf-8 _*-


from setuptools import setup

setup(name='font-converter',
      version='0.1',
      description='A font converter script',
      url='http://github.com/5uw1st/font-converter',
      author='5uw1st',
      author_email='j5uw1st@gmail.com',
      license='MIT',
      packages=['font_converter'],
      python_requires=">=3.6",
      install_requires=[
          'requests==2.20.1',
          'redis==4.4.4',
          'pytesseract==0.3.0',
          'Pillow==6.1.0',
      ],
      zip_safe=False)
