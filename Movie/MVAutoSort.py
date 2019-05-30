import json , requests ,random ,os,re,time
from lxml import etree
from opencc import OpenCC
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import gen as Gen

#Parameter
CHT_TW = True #優先取台灣譯名，且轉為繁體；若為False則為豆瓣上簡體中文標題
ZH_ENG = True #標題採中英混合；若為False則為僅中文標題 (當觸發ENGlen限制時則不保留英文標題)
regSt = True #地區縮寫，使用region.txt文件
UseProxy = False #是否使用Proxy
Remote = True #將路徑替換為遠端路徑 (讀取掛載信息，但在遠端上操作)
remote = "16tn:" #承上，遠端路徑
Local = True #使用本地搜尋
LogPath = "D:\\AutoSortLog" #默認為執行目錄
CSVName = "AutoSort"
SaveExcel = False #!未啟用
YearSort = True #老舊電影合併存放
Manual = 0 #0為全自動；1為遇到錯誤時切換為手動；2為自動搜尋手動確認 !未啟用
SearchMod = 0 #搜尋模式，0為使用原始資料夾名稱；1為 !未啟用
SubFolder = False #是否保留原始資料夾名稱，將其設為子資料夾 (當觸發pathlen限制時則不保留)
pathlen = 165 #路徑長度限制(僅計算資料夾)。若不想啟用輸入極大值即可，觸發後將不建立子資料夾
ENGlen = 65 #英文標題長度限制，若過長則僅保留中文標題。若不想啟用輸入極大值即可

#Initialize
dbapi = "https://api.douban.com/v2/movie/search?apikey=0dad551ec0f84ed02907ff5c42e8ec70&q="
genapi2 = "https://api.rhilip.info/tool/movieinfo/gen?url="
genapi3 = "https://api.nas.ink/infogen?url="
genapi1 = "http://api.ourhelp.club/infogen?url="
GenList = [genapi1,genapi2,genapi3]
genapinum = 0 #用來切換API
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
def SaveLog(save):
	if subtype == "movie":
		CSVName2 = "%s_Movie_%s.csv" % (CSVName,year)
	elif subtype == "tv":
		CSVName2 = "%s_TV_%s_%s.csv" % (CSVName,reg1,year)
	fname = LogPath+"\\"+CSVName2
	if not os.path.isfile(fname):
		save = "年份,地區,IMDb評分,豆瓣評分,中文標題,英文標題,其他標題,類型,IMDb_id,db_id\n"+save
	with open(fname,"a", encoding = 'utf-8-sig') as sdata: #寫檔
		sdata.write(save+"\n")

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
		'''key2 = key1[key1.rfind("]")+1:]
		print("Change :",key2)'''

		url = dbapi+key2
		resjson(url)
		if int(res['total']) == 1 and len(res['subjects'])==1: #Only 1 Result
			subtype = res['subjects'][0]['subtype']
			dblink = res['subjects'][0]['alt']
			year = res['subjects'][0]['year']
			if year in key1:
				return dblink
			else:
				print("*Error : Year doesn't match.")
		elif int(res['total']) == 0 or len(res['subjects'])==0: #找不到結果
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
	def GetInfo(dblink,proxy,switch=0):
		global year,subtype,reg1,reg2,reg3,save,genapinum
		if not Local:
			url2 = GenList[genapinum%3]+dblink
			try:
				r = requests.get(url2,headers={'User-Agent':ua.random},proxies=proxy,timeout=10)
			except requests.exceptions.ReadTimeout:
				print("*Error : Timeout")
				return ""
			if "Too Many Requests" in r.text:
				if switch < 3:
					switch += 1
					genapinum += 1
					print("*Error : Too Many Requests. Switch to another API.")
					Search.GetInfo(dblink,proxy,switch=switch)
				else:
					print("*Error : Too Many Requests. Wait for 300 seconds to retry")
					time.sleep(300)
					Search.GetInfo(dblink,proxy,switch=0)
				return
			'''proxy2 = get_proxy()
			Search.GetInfo(dblink,proxy2)
			return'''
		res = r.json() if not Local else Gen.gen_douban(dblink)
		if not res['success']: # Success
			if res['error'] == "GenHelp was banned by Douban." and switch<3:
				print("*Error :",res['error'],"Switch to another API.")
				switch += 1
				genapinum += 1
				Search.GetInfo(dblink,proxy,switch=switch)
				return
			else:
				print("*Error :",res['error'])
		else:
			year = res['year']
			titleZH = res['chinese_title'] #中文標題
			this_title = res['this_title'][0] #原始標題
			trans_title = res['trans_title'] #List 用來取台灣譯名
			aka = res['aka']
			episodes = res['episodes']
			if not subtype:
				subtype = "tv" if episodes else "movie"
			try:
				imdb_id = res['imdb_id']
			except KeyError:
				imdb_id = ""
			db_id,db_rating = "db_"+res['sid'],res['douban_rating_average']
			if not imdb_id:
				imdb_rating = ""
			else:
				try:
					imdb_rating = res['imdb_rating'][:res['imdb_rating'].find('/')]
				except:
					imdb_rating = 0
			mvid,rating = (imdb_id,imdb_rating )if imdb_id and imdb_rating else (db_id,db_rating)

			genre = "|".join(res['genre']) #List→str 類型
			region = res['region'] if type(res['region']) == type("str") else res['region'][0]
			reg1,reg2,reg3 = region,region,region
			for reg in regDic.keys(): #地區
				if reg == region:
					reg1 = reg
					reg2 = regDic[reg][0]
					reg3 = regDic[reg][1]
					break

			AllTitle1 = [titleZH]+[this_title]+aka+trans_title
			AllTitle2 = list(set(AllTitle1))
			AllTitle2.sort(key=AllTitle1.index)

			if CHT_TW: #繁體、台灣譯名
				if this_title != "" and reg1 == "台湾": #原始標題為中文地區是台灣)
					titleZH = this_title
				for trans in AllTitle2:
					if "(台)" in trans:
						if trans in AllTitle2:
							AllTitle2.remove(trans)
						titleZH = trans.replace("(台)","")
						break
				titleZH = OpenCC('s2twp').convert(titleZH)
				genre = OpenCC('s2twp').convert(genre)
				reg1 = OpenCC('s2twp').convert(reg1)
				for i in range(len(AllTitle2)):
					AllTitle2[i] = OpenCC('s2twp').convert(AllTitle2[i])
				if reg2 == reg3:
					reg2 = OpenCC('s2twp').convert(reg2)
			if ZH_ENG: #中英標題
				titleEN = ""
				for tt in AllTitle2:
					if not checkzh(tt):
						if tt in AllTitle2:
							AllTitle2.remove(tt)
						titleEN = tt.replace(" : ","：").replace(": ","：")
						break
				for tt in [titleZH]+aka:
					if checkzh(tt):
						if tt in AllTitle2:
							AllTitle2.remove(tt)
						titleZH = tt.replace(" : ","：").replace(": ","：")
						break
				title = (titleZH+" "+titleEN) if titleEN and len(titleEN) <= ENGlen else titleZH
			titleOT = AllTitle2

			region = reg2 if regSt else reg1
			titleOT = [] if not titleOT else titleOT
			save = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (year,reg1,imdb_rating,db_rating,titleZH,titleEN.replace(",","，"),"／".join(titleOT).replace(",","，"),genre,imdb_id,db_id)
			if float(rating):
				return "[%s][%s]%s(%s)(%s)(%s)" % (year,region,title,genre.replace("|","_"),rating,mvid)
			else:
				return "[%s][%s]%s(%s)(%s)" % (year,region,title,genre.replace("|","_"),mvid)
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
			subtype = ""
			print("\nFolder :",d)
			if re.search(r"\(db_(.+?)\)",d):
				dblink = "https://movie.douban.com/subject/%s/" % (re.search(r"\(db_(.+?)\)",d).group(1))
			elif re.search(r"\(tt(.+?)\)",d):
				imdb2db = "https://api.douban.com/v2/movie/imdb/%s?apikey=0df993c66c0c636e29ecbb5344252a4a" % ("tt"+re.search(r"\(tt(.+?)\)",d).group(1))
				resjson(imdb2db)
				dblink = res['alt'] if 'alt' in res.keys() else ""
			else:
				dblink = Search.DB(d)
			if dblink:
				print("dbLink :",dblink)
				name = Search.GetInfo(dblink,proxies)
			else:
				continue
			if name:
				print("Subtype:",subtype)
				print("Rename :",name)
			else:
				continue
			if YearSort:
				if int(year) > 2000:
					year = year
				elif 1991<=int(year) and int(year)<=2000:
					year = "1991-2000"
				elif 1981<=int(year) and int(year)<=1990:
					year = "1981-1990"
				elif int(year)<=1980:
					year = "1980以前"
			if subtype == "movie":
				Path = ("Movie\\%s\\%s" % (year,name))
			elif subtype == "tv":
				Path = ("TVSeries\\%s\\%s\\%s" % (reg1,year,name))
			path1 = mypath+"\\"+folder+"\\"+d
			path2 = mypath+"\\"+Path+"\\"+d if SubFolder else mypath+"\\"+Path
			if len(path2) > pathlen: #路徑長度
				path2 = mypath+"\\"+Path
			#command = ("rclone move -v \"%s\" \"%s\"" %(path1,path2))
			command = ("rclone move -v \"%s\" \"%s\" --log-file=%s" %(path1,path2,Logfile))
			command2 = ("rclone move -v \"%s\" \"%s\" --log-file=%s" %(path1,path2,Logfile))
			#os.popen(command)
			os.system(command)
			print("MoveTo :",path2)
			SaveLog("%s,%s,%s" % (save,d,Path))
