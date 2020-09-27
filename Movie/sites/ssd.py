import requests, re, os, time
from bs4 import BeautifulSoup
import http.cookiejar

def search(keyword, headers, cookies=".cookies\\ssd.txt"):
	if not os.path.exists(cookies):
		return False
	re_subname = re.match(r'(.+?)\.(mkv|mp4|ts|avi)', keyword) #去除副檔名
	key1 = key2 = re_subname.group(1) if re_subname else keyword
	re_brackets = re.search(r'\[(.+?)(\(.+\))?\].+(\d{4})', key2) #去除中括弧
	key2 = "{} {}".format(re_brackets.group(1), re_brackets.group(3)) if re_brackets else key2
	ssd_movie = re.search(r'(.+?)\d{0,2}(\(.+\))?\.(\d{4})(\..+)?.?￡.+', key2) #SSD-Movie
	key2 = "{} {} CMCT".format(ssd_movie.group(1),ssd_movie.group(3)) if ssd_movie else key2 
	ssd_tv = re.search(r'(.+)\.全\d+集|话\.(\d{4})\..+￡.+', key1) #SSD-TV
	key2 = "{} CMCT".format(ssd_tv.group(1)) if ssd_tv else key2
	ssd_version = re.search(r'(.+)( |\.)(.+版)', key2) #SSD-Version
	key2 = key2.replace(ssd_version.group(3),"") if ssd_version else key2
	key2 = key2.replace("！"," ").replace("!"," ").replace("-"," ").replace("\'"," ")
	url="https://springsunday.net/torrents.php?search="+key2

	cookies = http.cookiejar.MozillaCookieJar(cookies)
	cookies.load()
	response=requests.get(url,headers=headers,cookies=cookies)
	response.encoding = 'UTF-8'
	print(response.status_code) if response.status_code != 200 else print("",end="")

	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("table",{"class":"torrentname"})
	reslinks = ["https://springsunday.net/"+result.find("a").get("href") for result in results] #取得搜尋結果鏈接
	for reslink in reslinks:
		res=requests.get(reslink,headers=headers,cookies=cookies)
		res.encoding = 'UTF-8'
		print(res.status_code) if res.status_code != 200 else print("",end="")
		soup = BeautifulSoup(res.text, 'lxml')
		title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[SSD].","")
		if title == keyword:
			imdb_search = re.search(r"(http|https)://(www|us)\.imdb\.com/title/(tt\d+)",res.text)
			imdb_search2 = re.search(r'tt\d{6,}',res.text)
			db_search = re.search(r"https:\/\/(movie\.|www\.)?douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(3) if imdb_search else ""
			imdbid = imdb_search2.group() if not imdbid and imdb_search2 else imdbid
			if dblink or imdbid:
				return {'douban':dblink,'imdb':imdbid}	
		time.sleep(0.5)
	print(url) if len(reslinks) == 0 else print("",end="") #無結果時顯示搜尋關鍵字，搜尋邏輯優化用
	return False

if __name__ == '__main__':
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
	x = search("[1922].1922.2017.1080p.NF.WEB-DL.DDP.5.1.x264-CMCTV.mkv", headers)
	print(x)