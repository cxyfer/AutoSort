import requests,re,time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import http.cookiejar
import config

UA = UserAgent().random
def ourbits(keyword,cookies=config.ourbits,headers=config.headers):
	if not config.ourbits:
		return False
	key2 = keyword if not re.match(r'(.+?)\.(mkv|mp4|ts)', keyword) else re.match(r'(.+?)\.(mkv|mp4|ts)', keyword).group(1)
	url="https://ourbits.club/torrents.php?search="+key2
	cookies = http.cookiejar.MozillaCookieJar('.cookies\\ourbits.txt')
	cookies.load()
	response=requests.get(url,headers=headers,cookies=cookies)
	response.encoding = 'UTF-8' 
	print(response.status_code) if response.status_code != 200 else print("",end="")
	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("table",{"class":"torrentname"})
	reslinks = ["https://ourbits.club/"+result.find("a").get("href") for result in results] #取得搜尋結果鏈接
	for reslink in reslinks:
		res=requests.get(reslink,headers={'User-Agent':UA},cookies=cookies)
		res.encoding = 'UTF-8'
		print(res.status_code) if res.status_code != 200 else print("",end="")
		soup = BeautifulSoup(res.text, 'lxml')
		title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[OurBits].","")
		if title == keyword or title == key2:
			imdb_search = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",res.text)
			db_search = re.search(r"https:\/\/(movie\.)?douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(2) if imdb_search else ""
			try:
				dblink = 'https://movie.douban.com/subject/' + soup.find('div',{'id':'kdouban'}).get('data-doubanid') if not dblink else dblink
			except:
				pass
			if dblink or imdbid:
				return {'douban':dblink,'imdb':imdbid}	
	return False

def SSD(keyword,cookies=config.SSD):
	if not config.SSD:
		return False
	key2 = re.search(r'\[(.+?)\]', keyword).group(1) if re.search(r'\[(.+?)\]', keyword) else keyword #SSD無法直接用種子名稱搜尋
	key2 = re.search(r'(.+\.\d{4})\..+￡.+', keyword).group(1) if re.search(r'(.+\.\d{4})\..+￡.+', keyword) else key2 #SSD-Movie

	url="https://springsunday.net/torrents.php?search="+key2+" CMCT"
	cookies = http.cookiejar.MozillaCookieJar('.cookies\\ssd.txt')
	cookies.load()
	response=requests.get(url,headers={'User-Agent':UA},cookies=cookies)
	response.encoding = 'UTF-8'
	print(response.status_code) if response.status_code != 200 else print("",end="")
	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("table",{"class":"torrentname"})
	reslinks = ["https://springsunday.net/"+result.find("a").get("href") for result in results] #取得搜尋結果鏈接

	for reslink in reslinks:
		res=requests.get(reslink,headers={'User-Agent':UA},cookies=cookies)
		res.encoding = 'UTF-8'
		print(res.status_code) if res.status_code != 200 else print("",end="")
		if res.status_code != 200 :
			#print(reslink)
			continue
		soup = BeautifulSoup(res.text, 'lxml')
		title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[SSD].","")
		if title == keyword:
			imdb_search = re.search(r"(http|https)://(www|us)\.imdb\.com/title/(tt\d+)",res.text)
			imdb_search2 = re.search(r'tt\d{6,}',res.text)
			db_search = re.search(r"https:\/\/(movie\.)?douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(3) if imdb_search else ""
			imdbid = imdb_search2.group() if not imdbid and imdb_search2 else imdbid
			if dblink or imdbid:
				return {'douban':dblink,'imdb':imdbid}	
		time.sleep(1)
	return False
def TJUPT(keyword,cookies=config.TJUPT,headers=config.headers):
	if not config.TJUPT:
		return False
	key1 = key2 = keyword if not re.match(r'(.+?)\.(mkv|mp4|ts)', keyword) else re.match(r'(.+?)\.(mkv|mp4|ts)', keyword).group(1)
	key2 = key2.replace("@"," ")
	url="https://www.tjupt.org/torrents.php?search="+key2
	cookies = http.cookiejar.MozillaCookieJar('.cookies\\tjupt.txt')
	cookies.load()
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
		title2 = soup.find("title").getText()
		title2 = re.search(r'\"\[.+\]\[.+\]\[(.+)\]\"', title2).group(1) if re.search(r'\"\[.+\]\[.+\]\[(.+)\]\"', title2) else title2

		if keyword==title or keyword==title2 or keyword==title2 or key1==title2:
			imdb_search = re.search(r"(http|https)://www\.imdb\.com/title/(tt\d+)",res.text)
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
	cookies = http.cookiejar.MozillaCookieJar('.cookies\\frds.txt')
	cookies.load()
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
			db_search = re.search(r"https:\/\/(movie\.)?douban\.com\/(subject|movie)\/(\d+)",res.text)
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
			db_search = re.search(r"https:\/\/(movie\.)?douban\.com\/(subject|movie)\/(\d+)",res.text)
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
		title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[PT].","")
		if title == keyword:
			imdb_search = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",res.text)
			db_search = re.search(r"https:\/\/(movie\.)?douban\.com\/(subject|movie)\/(\d+)",res.text)
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
	cookies = http.cookiejar.MozillaCookieJar('.cookies\\ttg.txt')
	cookies.load()
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
		ftitle = soup.find("h1").getText().replace("[email protected]","")
		subtitle = ftitle[ftitle.find("[")+1:ftitle.find("]")]
		if title == keyword or title == key2:
			imdb_search = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",res.text)
			db_search = re.search(r"https:\/\/(movie\.)?douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(2) if imdb_search else ""
			#標題
			search_name = ''
			title_search_1 = re.search(r"(.+) 全集",subtitle)
			title_search_2 = re.search(r"(\d{2})年( )?(\d{1,2}月|.季)( )?(.+劇) (.+) 全\d+(話|集)",subtitle)
			title_search_3 = re.search(r"(.+劇) (.+) 主演",subtitle)
			if title_search_1:
				search_name = title_search_1.group(1)
			elif title_search_2:
				year = title_search_2.group(1)
				search_name = title_search_2.group(6)+ " " + ("20"+year if int(year) < 30 else "19"+year)
			elif title_search_3:
				search_name = title_search_3.group(2)
			if dblink or imdbid or search_name:
				return {'douban':dblink,'imdb':imdbid,'title':search_name}	
	return False
def PTer(keyword,cookies=config.PTer,headers=config.headers):
	if not config.PTer:
		return False
	key2 = keyword if not re.match(r'(.+?)\.(mkv|mp4|ts)', keyword) else re.match(r'(.+?)\.(mkv|mp4|ts)', keyword).group(1)
	key2 = re.search(r'\[(.+?)\]', keyword).group(1) if re.search(r'\[(.+?)\]', keyword) else keyword

	url="https://pterclub.com/torrents.php?search="+key2
	cookies = http.cookiejar.MozillaCookieJar('.cookies\\pter.txt')
	cookies.load()
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
		if title == keyword or key2 in title:
			imdb_search = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",res.text)
			db_search = re.search(r"https:\/\/(movie\.)?douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(2) if imdb_search else ""
			if dblink or imdbid:
				return {'douban':dblink,'imdb':imdbid}	
	return False
def TCCF(keyword,cookies=config.TCCF,headers=config.headers):
	if not config.TCCF:
		return False
	key2 = keyword if not re.match(r'(.+?)\.(mkv|mp4|ts)', keyword) else re.match(r'(.+?)\.(mkv|mp4|ts)', keyword).group(1)
	url="https://et8.org/torrents.php?search="+key2
	cookies = http.cookiejar.MozillaCookieJar('.cookies\\tccf.txt')
	cookies.load()
	response=requests.get(url,headers=headers,cookies=cookies)
	response.encoding = 'UTF-8'
	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("table",{"class":"torrentname"})
	reslinks = ["https://et8.org/"+result.find("a").get("href") for result in results] #取得搜尋結果鏈接
	for reslink in reslinks:
		res=requests.get(reslink,headers=headers,cookies=cookies)
		res.encoding = 'UTF-8'
		soup = BeautifulSoup(res.text, 'lxml')
		title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[TCCF].","")
		if title == keyword or key2 in title:
			imdb_search = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",res.text)
			db_search = re.search(r"https:\/\/(movie\.)?douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(2) if imdb_search else ""
			if dblink or imdbid:
				return {'douban':dblink,'imdb':imdbid}	
	return False