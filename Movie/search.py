import requests,re,time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import config

UA = UserAgent().random
def ourbits(keyword,cookies=config.ourbits,headers=config.headers):
	if not config.ourbits:
		return False
	key2 = keyword if not re.match(r'(.+?)\.(mkv|mp4|ts)', keyword) else re.match(r'(.+?)\.(mkv|mp4|ts)', keyword).group(1)
	url="https://ourbits.club/torrents.php?search="+key2
	response=requests.get(url,headers=headers,cookies=cookies)
	response.encoding = 'UTF-8'
	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("table",{"class":"torrentname"})
	reslinks = ["https://ourbits.club/"+result.find("a").get("href") for result in results] #取得搜尋結果鏈接
	
	for reslink in reslinks:
		res=requests.get(reslink,headers={'User-Agent':UA},cookies=cookies)
		res.encoding = 'UTF-8'
		soup = BeautifulSoup(res.text, 'lxml')
		title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[OurBits].","")
		if title == keyword or title == key2:
			imdb_search = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",res.text)
			db_search = re.search(r"https:\/\/(movie\.)?douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(2) if imdb_search else ""
			if dblink or imdbid:
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
			db_search = re.search(r"https:\/\/(movie\.)?douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(2) if imdb_search else ""
			if dblink or imdbid:
				return {'douban':dblink,'imdb':imdbid}	
	return False
def TJUPT(keyword,cookies=config.TJUPT,headers=config.headers):
	if not config.TJUPT:
		return False
	key2 = keyword if not re.match(r'(.+?)\.(mkv|mp4|ts)', keyword) else re.match(r'(.+?)\.(mkv|mp4|ts)', keyword).group(1)
	url="https://www.tjupt.org/torrents.php?search="+key2
	response=requests.get(url,headers=headers,cookies=cookies)
	response.encoding = 'UTF-8'
	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("table",{"class":"torrentname"})
	reslinks = ["https://www.tjupt.org/"+result.find("a").get("href") for result in results] #取得搜尋結果鏈接
	for reslink in reslinks:
		res=requests.get(reslink,headers=headers,cookies=cookies)
		res.encoding = 'UTF-8'
		soup = BeautifulSoup(res.text, 'lxml')
		title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[TJUPT].","")
		if title == keyword:
			imdb_search = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",res.text)
			db_search = re.search(r"https:\/\/(movie\.)?douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(2) if imdb_search else ""
			if dblink or imdbid:
				return {'douban':dblink,'imdb':imdbid}	
	return False
def FRDS(keyword,cookies=config.FRDS,headers=config.headers):
	if not config.FRDS:
		return False
	key2 = re.search(r'\.?([A-Za-z0-9.\']+\.S\d+)', keyword).group(1) if re.search(r'\.?([A-Za-z0-9.\']+\.S\d+)', keyword) else keyword
	url="https://pt.keepfrds.com/torrents.php?search="+key2
	response=requests.get(url,headers=headers,cookies=cookies)
	response.encoding = 'UTF-8'
	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("table",{"class":"torrentname"})
	reslinks = ["https://pt.keepfrds.com/"+result.find("a").get("href") for result in results]
	for reslink in reslinks:
		res=requests.get(reslink,headers=headers,cookies=cookies)
		res.encoding = 'UTF-8'
		soup = BeautifulSoup(res.text, 'lxml')
		title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[FRDS].","")
		if title == keyword:
			imdb_search = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",res.text)
			db_search = re.search(r"https:\/\/movie\.douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(2) if imdb_search else ""
			if dblink or imdbid:
				return {'douban':dblink,'imdb':imdbid}	
	return False
def MTeam(keyword,cookies=config.MTeam,headers=config.headers): #未知錯誤，疑似cookies無法使用
	if not config.MTeam:
		return False
	key2 = re.search(r'\.?([A-Za-z0-9.\']+\.S\d+)', keyword).group(1) if re.search(r'\.?([A-Za-z0-9.\']+\.S\d+)', keyword) else keyword
	url="https://pt.m-team.cc/torrents.php?search="+ key2
	response=requests.get(url,headers=headers,cookies=cookies)
	response.encoding = 'UTF-8'
	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("table",{"class":"torrentname"})
	reslinks = ["https://pt.m-team.cc/"+result.find("a").get("href") for result in results] #取得搜尋結果鏈接
	for reslink in reslinks:
		res=requests.get(reslink,headers={'User-Agent':UA},cookies=cookies)
		res.encoding = 'UTF-8'
		soup = BeautifulSoup(res.text, 'lxml')
		try:
			title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[M-TEAM].","")
			subtitle = soup.find("td",{"class":"rowfollow","valign":"top"}).getText()
		except:
			print(soup)
			continue
		if title == keyword:
			imdb_search = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",res.text)
			db_search = re.search(r"https:\/\/movie\.douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(2) if imdb_search else ""
			if dblink or imdbid:
				return {'douban':dblink,'imdb':imdbid}	
			elif re.search(r"(:|：)(.+)\(",subtitle):
				return {'title':re.search(r"(:|：)(.+)\(",subtitle).group(2).strip()}
	return False
def PuTao(keyword,cookies=config.PuTao):
	if not config.PuTao:
		return False
	key2 = keyword if not re.match(r'(.+?)\.(mkv|mp4|ts)', keyword) else re.match(r'(.+?)\.(mkv|mp4|ts)', keyword).group(1)
	url="https://pt.sjtu.edu.cn/torrents.php?search="+key2
	response=requests.get(url,headers={'User-Agent':UA},cookies=cookies)
	response.encoding = 'UTF-8'
	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("table",{"class":"torrentname"})
	reslinks = ["https://pt.sjtu.edu.cn/"+result.find("a").get("href") for result in results] #取得搜尋結果鏈接
	for reslink in reslinks:
		res=requests.get(reslink,headers={'User-Agent':UA},cookies=cookies)
		res.encoding = 'UTF-8'
		soup = BeautifulSoup(res.text, 'lxml')
		title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[PTer].","")
		if title == keyword:
			imdb_search = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",res.text)
			db_search = re.search(r"https:\/\/movie\.douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(2) if imdb_search else ""
			if dblink or imdbid:
				return {'douban':dblink,'imdb':imdbid}	
	return False
def TTG(keyword,cookies=config.TTG):
	if not config.TTG:
		return False
	key2 = keyword if not re.match(r'(.+?)\.(mkv|mp4|ts)', keyword) else re.match(r'(.+?)\.(mkv|mp4|ts)', keyword).group(1)
	url="https://totheglory.im/browse.php?c=M&search_field="+key2
	response=requests.get(url,headers={'User-Agent':UA},cookies=cookies)
	response.encoding = 'UTF-8'
	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("div",{"class":"name_left"})
	reslinks = ["https://totheglory.im/"+result.find("a").get("href") for result in results] #取得搜尋結果鏈接
	for reslink in reslinks:
		res=requests.get(reslink,headers={'User-Agent':UA},cookies=cookies)
		res.encoding = 'UTF-8'
		soup = BeautifulSoup(res.text, 'lxml')
		title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[TTG] ","")
		if title == keyword:
			imdb_search = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",res.text)
			db_search = re.search(r"https:\/\/movie\.douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(2) if imdb_search else ""
			if dblink or imdbid:
				return {'douban':dblink,'imdb':imdbid}	
	return False
def PTer(keyword,cookies=config.PTer,headers=config.headers):
	if not config.PTer:
		return False
	key2 = keyword if not re.match(r'(.+?)\.(mkv|mp4|ts)', keyword) else re.match(r'(.+?)\.(mkv|mp4|ts)', keyword).group(1)
	url="https://pterclub.com/torrents.php?search="+key2
	response=requests.get(url,headers=headers,cookies=cookies)
	response.encoding = 'UTF-8'
	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("table",{"class":"torrentname"})
	reslinks = ["https://pterclub.com/"+result.find("a").get("href") for result in results] #取得搜尋結果鏈接

	for reslink in reslinks:
		res=requests.get(reslink,headers=headers,cookies=cookies)
		res.encoding = 'UTF-8'
		soup = BeautifulSoup(res.text, 'lxml')
		title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[PTer].","")
		if title == keyword:
			imdb_search = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",res.text)
			db_search = re.search(r"https:\/\/movie\.douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(2) if imdb_search else ""
			if dblink or imdbid:
				return {'douban':dblink,'imdb':imdbid}	
	return False