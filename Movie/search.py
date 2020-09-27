import requests,re,time
from bs4 import BeautifulSoup
#from fake_useragent import UserAgent
from user_agent import generate_user_agent
import http.cookiejar

import config
from sites import ourbits, ssd, tjupt, pter, frds, tccf

#UA = UserAgent().random
UA = generate_user_agent()

def PT(dirname):
	IMDbID, dblink, source = '', '', ''
	if not (IMDbID or dblink) and re.search(r"FRDS|Yumi",dirname): #From FRDS
		ptsearch = frds.search(dirname, config.headers, "sites\\.cookies\\frds.txt")
		if ptsearch:
			IMDbID = ptsearch['imdb'] if ptsearch['imdb'] else ""
			dblink = ptsearch['douban'] if ptsearch['douban'] else (imdb2db2(IMDbID) if IMDbID else "")
			return {'douban':dblink,'imdb':IMDbID,'source':'FRDS'}		
	if not (IMDbID or dblink) and re.search(r"BMDru",dirname): #From TCCF
		ptsearch = tccf.search(dirname, config.headers, "sites\\.cookies\\tccf.txt")
		if ptsearch:
			IMDbID = ptsearch['imdb'] if ptsearch['imdb'] else ""
			dblink = ptsearch['douban'] if ptsearch['douban'] else (imdb2db2(IMDbID) if IMDbID else "")
			return {'douban':dblink,'imdb':IMDbID,'source':'TCCF'}		
	if not (IMDbID or dblink) and re.search(r"(Ao|FLTTH|iLoveHD|iLoveTV|MGs|OurPad|OurTV|PbK|NTb|NTG)",dirname): #From Ourbits
		ptsearch = ourbits.search(dirname, config.headers, "sites\\.cookies\\ourbits.txt")
		if ptsearch:
			IMDbID = ptsearch['imdb'] if ptsearch['imdb'] else ""
			dblink = ptsearch['douban'] if ptsearch['douban'] else (imdb2db2(IMDbID) if IMDbID else "")
			return {'douban':dblink,'imdb':IMDbID,'source':'Ourbits'}
	if not (IMDbID or dblink) and re.search(r"CMCT|NTb|NTG",dirname): #From SSD
		ptsearch = ssd.search(dirname, config.headers, "sites\\.cookies\\ssd.txt")
		if ptsearch:
			IMDbID = ptsearch['imdb'] if ptsearch['imdb'] else ""
			dblink = ptsearch['douban'] if ptsearch['douban'] else (imdb2db2(IMDbID) if IMDbID else "")
			return {'douban':dblink,'imdb':IMDbID,'source':'SSD'}
	if not (IMDbID or dblink) and re.search(r"TJUPT|AOA|QAQ|PBO|DGF|NigulaSi|VCB-Studio",dirname): #From TJUPT
		ptsearch = tjupt.search(dirname, config.headers, "sites\\.cookies\\tjupt.txt")
		if ptsearch:
			IMDbID = ptsearch['imdb'] if ptsearch['imdb'] else ""
			dblink = ptsearch['douban'] if ptsearch['douban'] else (imdb2db2(IMDbID) if IMDbID else "")
			return {'douban':dblink,'imdb':IMDbID,'source':'TJUPT'}
	if not (IMDbID or dblink) and re.search(r"PTer|AREY|NTb|NTG|ExREN|FRDS|beAst|CHD|RBOF|recked89",dirname): #From PTer
		ptsearch = pter.search(dirname, config.headers, "sites\\.cookies\\pter.txt")
		if ptsearch:
			IMDbID = ptsearch['imdb'] if ptsearch['imdb'] else ""
			dblink = ptsearch['douban'] if ptsearch['douban'] else (imdb2db2(IMDbID) if IMDbID else "")
			return {'douban':dblink,'imdb':IMDbID,'source':'PTer'}
	return False
		
def imdb2db2(IMDbID,count=3):
	if count < 0:
		return ''
	url = "https://movie.douban.com/j/subject_suggest?q={}".format(IMDbID)
	cookies = http.cookiejar.MozillaCookieJar('sites\\.cookies\\douban.txt')
	cookies.load()
	res = requests.get(url,headers=config.headers,cookies=cookies)
	if '检测到有异常请求从你的 IP 发出' in res.text:
		print("*Error : IP banned by douban.")
		exit()
		return False
	res = res.json() # return dict
	try:
		dblink = re.search(r"https:\/\/(movie\.)?douban\.com\/(subject|movie)\/(\d+)",res[0]['url']).group(0)
		time.sleep(0.5)
		return dblink
	except:
		imdb2db2(IMDbID,count-1)
		return ''
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
	cookies = http.cookiejar.MozillaCookieJar('sites\\.cookies\\ttg.txt')
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
if __name__ == "__main__":
	x = imdb2db2("tt10027990")
	print(x)