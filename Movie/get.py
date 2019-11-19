# ！/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019-2020 GDST <gdst.tw@gmail.com>
import os ,re ,requests
from opencc import OpenCC
from fake_useragent import UserAgent
import config

ua = UserAgent()
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

def findnfo(path):
    if not os.path.isdir(path):
        return False
    for file in sorted(os.listdir(path)):
        filepath = "%s\\%s" % (path,file)
        if os.path.isfile(filepath) and ( re.match(r'.+?\.nfo', file) or re.match(r'.+?\.txt', file) ):
            with open(filepath, "r", encoding="latin-1") as data: 
                for line in data:
                    imdb_search = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",line)
                    if imdb_search:
                        return {'imdb':imdb_search.group(2)}
                    db_search = re.search(r"https:\/\/movie\.douban\.com\/(subject|movie)\/(\d+)",line)
                    if db_search:
                        return {'douban':db_search.group()}


def imdb2db(IMDbID):
    imdb2db = "https://api.douban.com/v2/movie/imdb/%s?apikey=0df993c66c0c636e29ecbb5344252a4a" % (IMDbID)
    res = resjson(imdb2db)
    dblink = res['alt'].replace("/movie/","/subject/")+"/" if 'alt' in res.keys() else ""
    return dblink
def IMDbInfo(IMDbID):
    rapidapi_imdb = "https://movie-database-imdb-alternative.p.rapidapi.com/?i=%s&r=json" % (IMDbID)
    payload = {"X-RapidAPI-Host": "movie-database-imdb-alternative.p.rapidapi.com",
                "X-RapidAPI-Key": config.Rapid_IMDb}
    try:
        res = requests.get(rapidapi_imdb,headers=payload).json()
        return res
    except Exception as e:
        return False

def IMDb2TMDb(IMDbID,lan="zh-TW"):
    global year,subtype,reg1,reg2,reg3,save
    IMDbRating = IMDbInfo(IMDbID)
    imdb2tmdb = "https://api.themoviedb.org/3/find/%s?api_key=%s&language=%s&external_source=imdb_id" % (IMDbID ,config.TMDbAPI,lan)
    res = resjson(imdb2tmdb)
    if not "status_message" in res.keys() :
        if len(res["movie_results"]) != 0 or len(res["tv_results"]) != 0: #Movie+TVS
            IMDb =IMDbInfo(IMDbID)
            year = IMDb['Year']
            titleIMDb = IMDb['Title']
            IMDbRating = IMDb['imdbRating'] if IMDb['imdbRating'] != "N/A" else "0"
            region = IMDb['Country'].replace(" ","").split(",")[0]
            subtype = IMDb['Type'] if IMDb['Type'] == "movie" else "tv"

            results = res['movie_results'][0] if subtype == "movie" else res['tv_results'][0]
            titleZH = results['title'] if subtype == "movie" else results['name'] #Movie為title、TVS為name
            titleEN = results['original_title'] if subtype == "movie" else results['original_name']
            if titleZH == titleEN and lan != "zh-CN":
                return IMDb2TMDb(IMDbID,lan="zh-CN") #若TW譯名不存在，返回CN譯名
            genre_ids = results['genre_ids']
            genres = "|".join([MVgenres[genre_id] for genre_id in genre_ids])
            TMDbID = "TMDbMV_%s" % (results['id'])
            TMDbRating = results['vote_average']

            for reg in regDicEN.keys(): #地區
                if reg == region:
                    reg1 = regDicEN[reg][0]
                    reg2 = regDicEN[reg][1]
                    reg3 = reg
                    break

            AllTitle1 = [titleEN]+[titleIMDb]
            AllTitle2 = list(set(AllTitle1))
            AllTitle2.sort(key=AllTitle1.index)

            if config.CHT_TW: #繁體、台灣譯名
                titleZH = OpenCC('s2twp').convert(titleZH)
                genres = OpenCC('s2twp').convert(genres)
                reg1 = OpenCC('s2twp').convert(reg1)
            if config.ZH_ENG: #中英標題
                titleEN = ""
                for tt in AllTitle2:
                    if not checkzh(tt):
                        if tt in AllTitle2:
                            AllTitle2.remove(tt)
                        titleEN = tt.replace(" : ","：").replace(": ","：")
                        break
            title = (titleZH+" "+ titleEN) if  titleIMDb and len(titleEN) <= config.ENGlen and titleZH != titleEN  else titleZH
            save = "%s\t%s\t%s\t%s\t\t%s\t%s\t%s\t%s\t%s\t%s" % (IMDbID,year,reg1,IMDbRating,titleZH,titleEN,"／".join(AllTitle2),genres,IMDbID,TMDbID)
            name = "[%s][%s]%s(%s)(%s)(%s)" % (year,reg2,title,genres.replace("|","_"),IMDbRating,IMDbID)
            return [subtype,year,reg1,name,save]

def IMDbInt():
    global MVgenres,TVgenres
    MVgenresAPI = "https://api.themoviedb.org/3/genre/movie/list?api_key=%s&language=zh_TW" % (config.TMDbAPI)
    genres = resjson(MVgenresAPI)['genres']
    MVgenres = {}
    for genre in genres:
        MVgenres[genre['id']] = genre['name']
    TVgenresAPI = "https://api.themoviedb.org/3/genre/tv/list?api_key=%s&language=zh_TW" % (config.TMDbAPI)
    genres = resjson(TVgenresAPI)['genres']
    TVgenres = {}
    for genre in genres:
        TVgenres[genre['id']] = genre['name']

IMDbInt()
print()