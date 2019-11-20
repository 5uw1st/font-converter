## Font-converter

### Installing
Install and update using pip:
```shell
>pip install -U font_converter
```

### Example
```python
from font_converter import FontConverter

url = "https://static.tianyancha.com/fonts-styles/fonts/95/95564734/tyc-num.woff"
t = FontConverter(url, debug=False)
_words = "踏形里花计咨询、社型花计咨询；关人形里花计"
ret = t.convert(words=_words)
print(_words, ret, sep="\n")
```

### TODO

- Support multi-process
- Easy inherit