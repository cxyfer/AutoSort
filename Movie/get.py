# ！/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019-2020 GDST <gdst.tw@gmail.com>
import os ,re ,requests
from fake_useragent import UserAgent

ua = UserAgent()

def resjson(url):
    r = requests.get(url,headers={'User-Agent':ua.random})
    res = r.json() # return dict
    return res

def nfo_imdb(path):
    for file in sorted(os.listdir(path)):
        filepath = "%s\\%s" % (path,file)
        if os.path.isfile(filepath) and re.match(r'.+?\.nfo', file):
            nfo = re.match(r'.+?\.nfo', file).group()
            with open(filepath, "r", encoding="latin-1") as data: 
                for line in data:
                    if re.search(r"http://www.imdb.com/title/(.+?)",line):
                        return re.search(r"http://www\.imdb\.com/title/(.+).",line).group(1)

def imdb2db(IMDbID):
    imdb2db = "https://api.douban.com/v2/movie/imdb/%s?apikey=0df993c66c0c636e29ecbb5344252a4a" % (IMDbID)
    res = resjson(imdb2db)
    dblink = res['alt'].replace("/movie/","/subject/")+"/" if 'alt' in res.keys() else ""
    return dblink