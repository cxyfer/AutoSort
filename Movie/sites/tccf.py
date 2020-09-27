import requests, re, os, time
from bs4 import BeautifulSoup
import http.cookiejar

def search(keyword, headers, cookies='.cookies\\tccf.txt'):
	if not os.path.exists(cookies):
		return False
	re_subname = re.match(r'(.+?)\.(mkv|mp4|ts|avi)', keyword) #去副檔名
	key1 = key2 = re_subname.group(1) if re_subname else keyword
	re_brackets = re.search(r'\[(.+?)\d{0,2}(\(.+\))?\].+(\d{4})', key2) #去除中括弧
	key2 = "{} {}".format(re_brackets.group(1), re_brackets.group(3)) if re_brackets else key2
	key2 = key2.replace("@"," ")
	key2 = key2.replace(".Complete."," ")
	url = "https://et8.org/torrents.php?search=" + key2

	cookies = http.cookiejar.MozillaCookieJar(cookies)
	cookies.load()
	response=requests.get(url,headers=headers,cookies=cookies)
	response.encoding = 'UTF-8'
	print(response.status_code) if response.status_code != 200 else print("",end="")

	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("table",{"class":"torrentname"})
	reslinks = ["https://et8.org/"+result.find("a").get("href") for result in results] #取得搜尋結果鏈接
	for reslink in reslinks:
		res=requests.get(reslink,headers=headers,cookies=cookies)
		res.encoding = 'UTF-8'
		print(response.status_code) if response.status_code != 200 else print("",end="")
		soup = BeautifulSoup(res.text, 'lxml')

		title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[TCCF].","")
		if title == keyword:
			imdb_search = re.search(r"(http|https)://www\.imdb\.com/title/(tt\d+)",res.text)
			db_search = re.search(r"https:\/\/(movie\.|www\.)?douban\.com\/(subject|movie)\/(\d+)",res.text)
			dblink = db_search.group() if db_search else ""
			imdbid = imdb_search.group(2) if imdb_search else ""
			if dblink or imdbid:
				return {'douban':dblink,'imdb':imdbid}	
	print(url) if len(reslinks) == 0 else print("",end="") #無結果時顯示搜尋關鍵字，搜尋邏輯優化用
	return False

if __name__ == '__main__':
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
	x = search("Tokyo.Olympiad.1965.Criterion.Collection.720p.BluRay.DD1.0.x264-BMDru", headers)
	print(x)