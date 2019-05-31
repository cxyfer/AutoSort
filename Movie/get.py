# ！/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019-2020 GDST <gdst.tw@gmail.com>
import os ,re ,requests
from opencc import OpenCC
from fake_useragent import UserAgent
import api as API

ua = UserAgent()
CHT_TW = True
ENGlen = 65
ZH_ENG =True
regDicEN = {}

with open("region.txt" , "r", encoding = 'utf-8-sig') as regdataEN: #地區縮寫對應
    regListEN = [l.strip().split(',') for l in regdataEN ]
for regEN in regListEN:
    regDicEN[regEN[-1]]=regEN[:-1]

def resjson(url):
    r = requests.get(url,headers={'User-Agent':ua.random})
    res = r.json() # return dict
    return res

def checkzh(text):
    for t in text:
        if ord(t) > 255:
            return True

def nfo_imdb(path):
    for file in sorted(os.listdir(path)):
        filepath = "%s\\%s" % (path,file)
        if os.path.isfile(filepath) and re.match(r'.+?\.nfo', file):
            nfo = re.match(r'.+?\.nfo', file).group()
            with open(filepath, "r", encoding="latin-1") as data: 
                for line in data:
                    if re.search(r"http://www.imdb.com/title/(.+?)",line):
                        return re.search(r"http://www\.imdb\.com/title/(tt\d+)",line).group(1)

def imdb2db(IMDbID):
    imdb2db = "https://api.douban.com/v2/movie/imdb/%s?apikey=0df993c66c0c636e29ecbb5344252a4a" % (IMDbID)
    res = resjson(imdb2db)
    dblink = res['alt'].replace("/movie/","/subject/")+"/" if 'alt' in res.keys() else ""
    return dblink
def IMDbInfo(IMDbID):
    rapidapi_imdb = "https://movie-database-imdb-alternative.p.rapidapi.com/?i=%s&r=json" % (IMDbID)
    payload = {"X-RapidAPI-Host": "movie-database-imdb-alternative.p.rapidapi.com",
                "X-RapidAPI-Key": API.Rapid_IMDb}
    try:
        res = requests.get(rapidapi_imdb,headers=payload).json()
        return res
    except Exception as e:
        return False

def IMDb2TMDb(IMDbID):
    global year,subtype,reg1,reg2,reg3,save
    IMDbRating = IMDbInfo(IMDbID)
    imdb2tmdb = "https://api.themoviedb.org/3/find/%s?api_key=%s&language=zh-TW&external_source=imdb_id" % (IMDbID ,API.TMDbAPI)
    res = resjson(imdb2tmdb)
    if not "status_message" in res.keys() :
        if len(res["movie_results"]) != 0:
            IMDb =IMDbInfo(IMDbID)
            results = res['movie_results'][0] 

            titleZH = results['title']
            titleEN = results['original_title']
            genre_ids = results['genre_ids']
            genres = "|".join([MVgenres[genre_id] for genre_id in genre_ids])
            TMDbID = "TMDbMV_%s" % (results['id'])
            TMDbRating = results['vote_average']

            year = IMDb['Year']
            titleIMDb = IMDb['Title']
            IMDbRating = IMDb['imdbRating']
            region = IMDb['Country'].replace(" ","").split(",")[0]
            subtype = IMDb['Type']

            for reg in regDicEN.keys(): #地區
                if reg == region:
                    reg1 = regDicEN[reg][0]
                    reg2 = regDicEN[reg][1]
                    reg3 = reg
                    break

            AllTitle1 = [titleEN]+[titleIMDb]
            AllTitle2 = list(set(AllTitle1))
            AllTitle2.sort(key=AllTitle1.index)

            if CHT_TW: #繁體、台灣譯名
                titleZH = OpenCC('s2twp').convert(titleZH)
                genres = OpenCC('s2twp').convert(genres)
                reg1 = OpenCC('s2twp').convert(reg1)
            if ZH_ENG: #中英標題
                titleEN = ""
                for tt in AllTitle2:
                    if not checkzh(tt):
                        if tt in AllTitle2:
                            AllTitle2.remove(tt)
                        titleEN = tt.replace(" : ","：").replace(": ","：")
                        break
            title = (titleZH+" "+ titleIMDb) if  titleIMDb and len(titleIMDb) <= ENGlen else titleZH
            save = "%s,%s,%s,,%s,%s,%s,%s,%s,%s" % (year,reg1,IMDbRating,titleZH,titleEN.replace(",","，"),"／".join(AllTitle2).replace(",","，"),genres,IMDbID,TMDbID)
            name = "[%s][%s]%s(%s)(%s)(%s)" % (year,reg2,title,genres.replace("|","_"),IMDbRating,IMDbID)
            return [subtype,year,reg1,name,save]

def IMDbInt():
    global MVgenres,TVgenres
    MVgenresAPI = "https://api.themoviedb.org/3/genre/movie/list?api_key=%s&language=zh_TW" % (API.TMDbAPI)
    genres = resjson(MVgenresAPI)['genres']
    MVgenres = {}
    for genre in genres:
        MVgenres[genre['id']] = genre['name']
    TVgenresAPI = "https://api.themoviedb.org/3/genre/tv/list?api_key=%s&language=zh_TW" % (API.TMDbAPI)
    genres = resjson(TVgenresAPI)['genres']
    TVgenres = {}
    for genre in genres:
        TVgenres[genre['id']] = genre['name']

IMDbInt()
