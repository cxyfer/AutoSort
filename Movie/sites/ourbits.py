import requests, re, os, time
from bs4 import BeautifulSoup
import http.cookiejar

def search(keyword, headers, cookies='.cookies\\ourbits.txt'):
	if not os.path.exists(cookies):
		return False
	re_subname = re.match(r'(.+?)\.(mkv|mp4|ts|avi)', keyword) #去副檔名
	key2 = re_subname.group(1) if re_subname else keyword
	key2 = key2.replace(".Complete."," ").replace(".SUBBED."," ")
	key2 = key2.replace("第"," 第 ").replace("季"," 季 ")
	url="https://ourbits.club/torrents.php?search="+key2

	cookies = http.cookiejar.MozillaCookieJar(cookies)
	cookies.load()
	response=requests.get(url,headers=headers,cookies=cookies)
	response.encoding = 'UTF-8'
	print(response.status_code) if response.status_code != 200 else print("",end="")

	soup = BeautifulSoup(response.text, 'lxml')
	results = soup.find_all("table",{"class":"torrentname"})
	reslinks = ["https://ourbits.club/"+result.find("a").get("href") for result in results] #取得搜尋結果鏈接
	for reslink in reslinks:
		res=requests.get(reslink,headers=headers,cookies=cookies)
		res.encoding = 'UTF-8'
		print(res.status_code) if res.status_code != 200 else print("",end="")
		soup = BeautifulSoup(res.text, 'lxml')
		title = soup.find("a",{"class":"index"}).getText().replace(".torrent","").replace("[OurBits].","")

		if title == keyword or title == key2:
			imdb_search = re.search(r"(http|https)://www.imdb.com/title/(tt\d+)",res.text)
			douban_search = re.search(r"https:\/\/(movie\.|www\.)?douban\.com\/(subject|movie)\/(\d+)",res.text)
			imdbid = imdb_search.group(2) if imdb_search else ""
			dblink = douban_search.group() if douban_search else ""
			try:
				dblink = 'https://movie.douban.com/subject/' + soup.find('div',{'id':'kdouban'}).get('data-doubanid') if not dblink else dblink
			except:
				pass
			if dblink or imdbid:
				return {'douban':dblink,'imdb':imdbid}	
	print(url) if len(reslinks) == 0 else print("",end="") #搜尋邏輯優化用
	return False

if __name__ == '__main__':
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
	x = search("All.Together.Now.2020.1080p.NF.WEB-DL.DDP5.1.H264-Ao", headers)
	print(x)