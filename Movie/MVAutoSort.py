import json , requests ,random ,os,re
from lxml import etree
from opencc import OpenCC
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

#Parameter
CHT_TW = True #優先取台灣譯名，且轉為繁體；若為False則為豆瓣上簡體中文標題
ZH_ENG = True #標題採中英混合；若為False則為僅中文標題 (當觸發ENGlen限制時則不保留英文標題)
regSt = True #地區縮寫，使用region.txt文件
UseProxy = False #是否使用Proxy
Remote = False #將路徑替換為遠端路徑 (讀取掛載信息，但在遠端上操作)
remote = ":" #承上，遠端路徑
LogPath = "D:\\" #默認為執行目錄
SaveExcel = False #!未啟用
YearSort = True #老舊電影合併存放
Manual = 0 #0為全自動；1為遇到錯誤時切換為手動；2為自動搜尋手動確認 !未啟用
SearchMod = 0 #搜尋模式，0為使用原始資料夾名稱；1為 !未啟用
SubFolder = True #是否保留原始資料夾名稱，將其設為子資料夾 (當觸發pathlen限制時則不保留)
pathlen = 165 #路徑長度限制(僅計算資料夾)。若不想啟用輸入極大值即可，觸發後將不建立子資料夾
ENGlen = 65 #英文標題長度限制，若過長則僅保留中文標題。若不想啟用輸入極大值即可

#Initialize
dbapi = "https://api.douban.com/v2/movie/search?q="
genapi = "https://api.rhilip.info/tool/movieinfo/gen?url="
ua = UserAgent()
regDic = {}

with open("folder.txt" , "r", encoding = 'utf-8-sig') as data: #只在這些子資料夾執行
	folderList = [l.strip() for l in data ]
with open("region.txt" , "r", encoding = 'utf-8-sig') as regdata: #地區縮寫對應
	regList = [l.strip().split(',') for l in regdata ]
for reg in regList:
	regDic[reg[0]]=reg[1:]

#Function
def resjson(url):
	global res
	r = requests.get(url,headers={'User-Agent':ua.random})
	res = r.json() # return dict
def checkzh(text):
	for t in text:
		if ord(t) > 255:
			return True
def built_proxy():
	global ProxyList
	ProxyList = []
	res = requests.get('https://free-proxy-list.net/', headers={'User-Agent':ua.random})
	soup = BeautifulSoup(res.text,"lxml")
	for items in soup.select("tbody tr"):
		proxy = ':'.join([item.text for item in items.select("td")[:2]])
		ProxyList += [proxy]
def get_proxy():
	random.shuffle(ProxyList)
	proxy = ProxyList[0]
	print("Proxy  :",proxy,end=", ")
	proxies = {
			"http": "http://"+proxy,
			"https": "http://"+proxy
				}
	url = 'https://httpbin.org/ip'
	try:
		response = requests.get(url,proxies=proxies, headers={'User-Agent':ua.random})
		res = response.json()
		print(True,",",res['origin'])
		return proxies
	except:
		print(False)
		get_proxy()
	return
def move(src,dst):
	for root, dirs, files in os.walk(src):
		for d in dirs:
			src_dir = root+"\\"+d
			dst_dir = src_dir.replace(src,dst)
			if not os.path.exists(dst_dir):
				os.mkdir(dst_dir)
		for file in files:
			src_path = root+"\\"+file
			dst_path = src_path.replace(src,dst)
			if not os.path.exists(dst_path):
				os.rename(src_path,dst_path)

class Search:
	def DB(key1,Manual=False): #Manual為手動整理參數 !暫未完成
		global subtype , dblink
		key2 = key1
		for i in range(len(key1),0,-1): #去除冗贅資料，以便查詢
			if i-1 > 0 and key1[i-4:i].isdigit():
				key2 = key1[:key1.find(key1[i-4:i])]
				if key2 != "":
					print("Change :",key2)
				else:
					key2 = key1
				break
		url = dbapi+key2
		resjson(url)
		if int(res['total']) == 1: #Only 1 Result
			subtype = res['subjects'][0]['subtype']
			dblink = res['subjects'][0]['alt']
			year = res['subjects'][0]['year']
			if year in key1:
				return dblink
			else:
				print("*Error : Year doesn't match.")
		elif int(res['total']) == 0: #找不到結果
			print("*Error : No results found.")
			return False
		elif int(res['total']) > 1 : #過多結果
			for subject in res['subjects']: #例外處理-過多資料-年份比對
				if subject['year'] in key1:
					subtype = subject['subtype']
					dblink = subject['alt']
					return dblink
			print("*Error : No results found.")
			return False
	def GetInfo(dblink,proxy):
		global year,reg1,reg2,reg3
		url2 = genapi+dblink
		r = requests.get(url2,headers={'User-Agent':ua.random},proxies=proxy)
		if "Too Many Requests" in r.text:
			print("Too Many Requests")
			proxy2 = get_proxy()
			Search.GetInfo(dblink,proxy2)
			return
		res = r.json()
		if res['success']: # Success
			year = res['year']
			title = res['chinese_title'] #中文標題
			foreign_title = res['foreign_title'] #原始標題
			trans_title = res['trans_title'] #List 用來取台灣譯名
			aka = res['aka']
			genre = "_".join(res['genre']) #List→str 類型
			reg1,reg2,reg3 = res['region'][0],res['region'][0],res['region'][0]
			for reg in regDic.keys(): #地區
				if reg == res['region'][0]:
					reg1 = reg
					reg2 = regDic[reg][0]
					reg3 = regDic[reg][1]
					break
			try:
				mvid = res['imdb_id']
				rating = res['imdb_rating'][:res['imdb_rating'].find('/')]
			except:
				mvid = 'db_'+res['sid']
				rating = res['douban_rating_average']

			if CHT_TW: #繁體、台灣譯名
				if foreign_title != "" and reg1 == "台湾": #原始標題為中文地區是台灣)
					title = foreign_title
				for trans in trans_title:
					if "(台)" in trans:
						title = trans.replace("(台)","")
						break
				title = OpenCC('s2twp').convert(title)
				genre = OpenCC('s2twp').convert(genre)
				reg1 = OpenCC('s2twp').convert(reg1)
				if reg2 == reg3:
					reg2 = OpenCC('s2twp').convert(reg2)
			if ZH_ENG: #中英標題
				title2 = False
				for tt in [title]+[foreign_title]+aka+trans_title:
					if not checkzh(tt):
						title2 = tt.replace(" : ","：").replace(": ","：")
						break
				for tt in [title]+aka:
					if checkzh(tt):
						title = tt.replace(" : ","：").replace(": ","：")
						break
				title = (title+" "+title2) if title2 and len(title2) <= ENGlen else title

			region = reg2 if regSt else reg1
			return "[%s][%s]%s(%s)(%s)(%s)" % (year,region,title,genre,rating,mvid)
'''Test
key = "Apollo 11 2019 BluRay 720p DTS x264-MTeam"
dblink = Search.DB(key)
print("dbLink :",dblink)
if dblink:
	print(Search.GetInfo(dblink,proxies))'''

built_proxy()
proxies = get_proxy() if UseProxy else ""
mypath = os.getcwd() if not Remote else remote #執行目錄
Logfile = LogPath+"\\move.log" if LogPath else "move.log"

for folder in folderList:
	if os.path.isdir(folder): #如果指定的資料夾存在
		for d in os.listdir(folder):

			print("\nFolder :",d) 
			dblink = Search.DB(d)
			if dblink:
				print("dbLink :",dblink)
				print("Subtype:",subtype)
				name = Search.GetInfo(dblink,proxies)
			else:
				continue
			if name:
				print("Rename :",name)
			else:
				continue
			if subtype == "movie":
				if YearSort:
					if int(year) > 2000:
						year = year
					elif 1991<=int(year) and int(year)<=2000:
						year = "1991-2000"
					elif 1981<=int(year) and int(year)<=1990:
						year = "1981-1990"
					elif int(year)<=1980:
						year = "1980以前"
				Path = ("Movie\\%s\\%s" % (year,name))
			elif subtype == "tv":
				Path = ("TVSeries\\%s\\%s\\%s" % (reg1,year,name))
			path1 = mypath+"\\"+folder+"\\"+d
			path2 = mypath+"\\"+Path+"\\"+d if SubFolder else mypath+"\\"+Path
			if len(path2) > pathlen: #路徑長度
				path2 = mypath+"\\"+Path

			#command = ("rclone move -v \"%s\" \"%s\"" %(path1,path2))
			command = ("rclone move -v \"%s\" \"%s\" --log-file=%s" %(path1,path2,Logfile))
			#os.popen(command)
			os.system(command)
			print("MoveTo :",path2)
