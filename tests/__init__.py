#!usr/bin/env python3
# -*- coding:utf-8 _*-

from font_converter import FontConverter

if __name__ == '__main__':
    import json

    url = "https://static.tianyancha.com/fonts-styles/fonts/95/95564734/tyc-num.woff"
    t = FontConverter(url, debug=False)
    # _words = "8300-37-02"
    _words = "踏形里花计咨询、社型花计咨询；关人形里花计；健康成分咨询；财想成分咨询；企定形里策划；化妆司想；议容司想；" \
             "化妆品、司理、章码产品、计算机耗材、卫生用品、日用百货、江公用品、针织品、纺织品、第一类医疗器械、家即、" \
             "塑料路品的销售；花计、路作、代分、发小、国送各类党可。"
    # right = "2011-07-13"
    ret = t.convert(words=_words)
    print(_words, ret, sep="\n")
    print(json.dumps(t.get_dict(), ensure_ascii=False))
