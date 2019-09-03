import requests,re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import config

UA = UserAgent().random

def ourbits(keyword,cookies=config.ourbits):
	if not config.ourbits:
		return False
	url="https://ourbits.club/torrents.php?search="+keyword
	response=requests.get(url,headers={'User-Agent':UA},cookies=cookies)
	response.encoding = 'UTF-8'
	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("table",{"class":"torrentname"})
	reslinks = ["https://ourbits.club/"+result.find("a").get("href") for result in results] #取得搜尋結果鏈接
	
	for reslink in reslinks:
		response=requests.get(reslink,headers={'User-Agent':UA},cookies=cookies)
		response.encoding = 'UTF-8'
		soup = BeautifulSoup(response.text, 'lxml')
		title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[OurBits].","")
		if title == keyword:
			db = soup.find("div",{"id":"kdouban"})
			imdb = soup.find("div",{"class":"imdbnew"})
			dblink = "https://movie.douban.com/subject/%s/" % (db.get("data-doubanid")) if db else ""
			imdbid = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",imdb.find("a").get("href")).group(2) if imdb else ""
			return {'douban':dblink,'imdb':imdbid}
	return False
def SSD(keyword,cookies=config.SSD):
	if not config.SSD:
		return False
	key2 = re.search(r'\[(.+?)\]', keyword).group(1) if re.search(r'\[(.+?)\]', keyword) else keyword[:keyword.find(".")] #SSD無法直接用種子名稱搜尋
	url="https://springsunday.net/torrents.php?search="+key2
	response=requests.get(url,headers={'User-Agent':UA},cookies=cookies)
	response.encoding = 'UTF-8'
	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("table",{"class":"torrentname"})
	reslinks = ["https://springsunday.net/"+result.find("a").get("href") for result in results] #取得搜尋結果鏈接
	for reslink in reslinks:
		res=requests.get(reslink,headers={'User-Agent':UA},cookies=cookies)
		res.encoding = 'UTF-8'
		soup = BeautifulSoup(res.text, 'lxml')
		title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[SSD].","")
		if title == keyword:
			imdb_search = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",res.text)
			db_search = re.search(r"https:\/\/movie\.douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(2) if imdb_search else ""
			return {'douban':dblink,'imdb':imdbid}
	return False
def TJUPT(keyword,cookies=config.TJUPT):
	if not config.TJUPT:
		return False
	url="https://www.tjupt.org/torrents.php?search="+keyword
	response=requests.get(url,headers={'User-Agent':UA},cookies=cookies)
	response.encoding = 'UTF-8'
	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("table",{"class":"torrentname"})
	reslinks = ["https://www.tjupt.org/"+result.find("a").get("href") for result in results] #取得搜尋結果鏈接
	for reslink in reslinks:
		res=requests.get(reslink,headers={'User-Agent':UA},cookies=cookies)
		res.encoding = 'UTF-8'
		soup = BeautifulSoup(res.text, 'lxml')
		title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[TJUPT].","")
		if title == keyword:
			imdb_search = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",res.text)
			db_search = re.search(r"https:\/\/movie\.douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(2) if imdb_search else ""
			return {'douban':dblink,'imdb':imdbid}
	return False