# ！/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2017-2020 Rhilip <rhilipruan@gmail.com>

import re,time
import json
import random
import requests
from bs4 import BeautifulSoup
from html2bbcode.parser import HTML2BBCode
import http.cookiejar

__version__ = "0.4.5"
__author__ = "Rhilip"

douban_apikey_list = [
    "02646d3fb69a52ff072d47bf23cef8fd",
    "0b2bdeda43b5688921839c8ecb20399b",
    "0dad551ec0f84ed02907ff5c42e8ec70",
    "0df993c66c0c636e29ecbb5344252a4a"
]
    #"07c78782db00a121175696889101e363"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/61.0.3163.100 Safari/537.36 ',
    "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8"
}

cookies = http.cookiejar.MozillaCookieJar('.cookies\\douban.txt')
cookies.load()

def get_db_apikey() -> str:
    return random.choice(douban_apikey_list)

def get_page(url: str, json_=False, jsonp_=False, bs_=False, text_=False, **kwargs):
    kwargs.setdefault("headers", headers)
    page = requests.get(url, **kwargs,cookies=cookies)

    page.encoding = "utf-8"
    page_text = page.text
    if json_:
        try:
            return page.json()
        except:
            time.sleep(0.5)
            return get_page(url,json_=True)
    elif jsonp_:
        start_idx = page_text.find('(')
        end_idx = page_text.rfind(')')
        return json.loads(page_text[start_idx + 1:end_idx])
    elif bs_:
        return BeautifulSoup(page.text, "lxml")
    elif text_:
        return page_text
    else:
        return page


def html2ubb(html: str) -> str:
    return str(HTML2BBCode().feed(html))

def get_num_from_string(raw):
    return int(re.search('[\d,]+', raw).group(0).replace(',', ''))

def gen_douban(dblink):
    data = {}
    sid = re.search(r"https:\/\/(movie\.)?douban\.com\/(subject|movie)\/(\d+)",dblink).group(3)
    data['sid'] = sid
    douban_page = get_page(dblink, bs_=True)
    douban_api_json = get_page(
        'https://api.douban.com/v2/movie/{}'.format(sid),
        params={'apikey': get_db_apikey()},
        json_=True
    )
    douban_abstract_json = get_page('https://movie.douban.com/j/subject_abstract?subject_id={}'.format(sid), json_=True)

    data['success'] = False
    if "msg" in douban_api_json and (douban_api_json["msg"] != 'invalid_credencial2'): #API失效應急
        data["error"] = douban_api_json["msg"]
    elif str(douban_page).find("检测到有异常请求") > -1:
        data["error"] = "GenHelp was banned by Douban."
        data['exit'] = True
    elif douban_page.title.text == "页面不存在":
        data["error"] = "The corresponding resource does not exist."
    else:
        data["douban_link"] = dblink
        data['success'] = True
        def fetch(node):
            return node.next_element.next_element.strip()
        # 对主页面进行解析
        data["chinese_title"] = (douban_page.title.text.replace("(豆瓣)", "").strip())
        data["foreign_title"] = (douban_page.find("span", property="v:itemreviewed").text
                                 .replace(data["chinese_title"], '').strip()) if douban_page.find("span", property="v:itemreviewed") else ""

        aka_anchor = douban_page.find("span", class_="pl", text=re.compile("又名"))
        data["aka"] = sorted(fetch(aka_anchor).split(' / ')) if aka_anchor else []

        if data["foreign_title"]:
            trans_title = data["chinese_title"] + (('/' + "/".join(data["aka"])) if data["aka"] else "")
            this_title = data["foreign_title"]
        else:
            trans_title = "/".join(data["aka"]) if data["aka"] else ""
            this_title = data["chinese_title"]

        data["trans_title"] = trans_title.split("/")
        data["this_title"] = this_title.split("/")

        region_anchor = douban_page.find("span", class_="pl", text=re.compile("制片国家/地区"))
        language_anchor = douban_page.find("span", class_="pl", text=re.compile("语言"))
        seasons_anchor = douban_page.find("span", class_="pl", text=re.compile("季数"))
        episodes_anchor = douban_page.find("span", class_="pl", text=re.compile("集数"))
        imdb_link_anchor = douban_page.find("a", text=re.compile("tt\d+"))
        year_anchor = douban_page.find("span", class_="year")

        data["year"] = douban_page.find("span", class_="year").text[1:-1] if year_anchor else ""  # 年代
        data["region"] = fetch(region_anchor).split(" / ") if region_anchor else []  # 产地
        data["genre"] = list(map(lambda l: l.text.strip(), douban_page.find_all("span", property="v:genre")))  # 类别
        data["language"] = fetch(language_anchor).split(" / ") if language_anchor else []  # 语言
        data["playdate"] = sorted(map(lambda l: l.text.strip(),  # 上映日期
                                          douban_page.find_all("span", property="v:initialReleaseDate")))
        data["imdb_link"] = imdb_link_anchor.attrs["href"] if imdb_link_anchor else ""  # IMDb链接
        data["imdb_id"] = imdb_link_anchor.text if imdb_link_anchor else ""  # IMDb号
        data["episodes"] = fetch(episodes_anchor) if episodes_anchor else ""  # 集数
        season_check = douban_page.find("select", id="season")
        data["seasons_list"] = [option.get("value") for option in douban_page.find("select", id="season").find_all("option")] if seasons_anchor and season_check else []  #季數
        data["seasons"] = douban_page.find("select", id="season").find_all("option")[-1].getText() if seasons_anchor and season_check else ""  #季數

        duration_anchor = douban_page.find("span", class_="pl", text=re.compile("单集片长"))
        runtime_anchor = douban_page.find("span", property="v:runtime")

        duration = ""  # 片长
        if duration_anchor:
            duration = fetch(duration_anchor)
        elif runtime_anchor:
            duration = runtime_anchor.text.strip()
        data["duration"] = duration

        # 请求其他资源
        if data["imdb_link"]:  # 该影片在豆瓣上存在IMDb链接
            imdb_source = ("https://p.media-imdb.com/static-content/documents/v1/title/{}/ratings%3Fjsonp="
                           "imdb.rating.run:imdb.api.title.ratings/data.json".format(data["imdb_id"]))
            try:
                imdb_json = get_page(imdb_source, jsonp_=True)  # 通过IMDb的API获取信息，（经常超时555555）
                imdb_average_rating = imdb_json["resource"]["rating"]
                imdb_votes = imdb_json["resource"]["ratingCount"]
                if imdb_average_rating and imdb_votes:
                    data["imdb_rating"] = "{}/10 from {} users".format(imdb_average_rating, imdb_votes)
            except Exception as err:
                pass

        # 豆瓣评分，简介，海报，导演，编剧，演员，标签
        '''data["douban_rating_average"] = douban_average_rating = douban_api_json["rating"]["average"] or 0
        data["douban_votes"] = douban_votes = douban_api_json["rating"]["numRaters"] or 0
        data["douban_rating"] = "{}/10 from {} users".format(douban_average_rating, douban_votes)
        data["tags"] = list(map(lambda member: member["name"], douban_api_json["tags"]))'''

        abstract_subject = douban_abstract_json["subject"]
        try:
            data["douban_rating_average"] = douban_average_rating = douban_page.find("strong", property="v:average").text or 0
            data["douban_votes"] = douban_votes = douban_page.find("span", property="v:votes").text or 0
        except:
            data["douban_rating_average"] = douban_average_rating = abstract_subject["rate"] or 0
        data["year"] = abstract_subject["release_year"] if not data["year"] else data["year"]
        data["subtype"] = 'tv' if abstract_subject['is_tv'] or data["episodes"] or abstract_subject['subtype'].lower() == 'tv' else 'movie'

    # 将清洗的数据一并发出
    return data
