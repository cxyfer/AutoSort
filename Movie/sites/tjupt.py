import requests, re, os, time
from bs4 import BeautifulSoup
import http.cookiejar

def decode(cfemail):
	enc = bytes.fromhex(cfemail)
	return bytes([c ^ enc[0] for c in enc[1:]]).decode('utf8')

def search(keyword, headers, cookies='.cookies\\tjupt.txt'):
	if not os.path.exists(cookies):
		return False
	re_subname = re.match(r'(.+?)\.(mkv|mp4|ts|avi)', keyword) #去副檔名
	key1 = key2 = re_subname.group(1) if re_subname else keyword
	key2 = key2.replace("@"," ")
	key2 = key2.replace(".Complete."," ")
	url="https://www.tjupt.org/torrents.php?search="+key2
	print(url)

	cookies = http.cookiejar.MozillaCookieJar(cookies)
	cookies.load()
	response=requests.get(url,headers=headers,cookies=cookies)
	response.encoding = 'UTF-8'
	print(response.status_code) if response.status_code != 200 else print("",end="")

	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("table",{"class":"torrentname"})
	reslinks = ["https://www.tjupt.org/"+result.find("a").get("href") for result in results] #取得搜尋結果鏈接
	for reslink in reslinks:
		res=requests.get(reslink,headers=headers,cookies=cookies)
		res.encoding = 'UTF-8'
		print(res.status_code) if res.status_code != 200 else print("",end="")

		soup = BeautifulSoup(res.text, 'lxml')
		decrypted = decode(soup.find("span",{"class":"__cf_email__"}).get("data-cfemail")) #cf_email
		title = soup.find("a",{"class":"index"}).getText().replace("[email protected]",decrypted).replace("[TJUPT].","").replace(".torrent","")

		if title == keyword or title == key1:
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
	x = search("Liu.Lao.Gen.S02.1080p.WEB-DL.H264.AAC-RushB@TJUPT", headers)
	print(x)