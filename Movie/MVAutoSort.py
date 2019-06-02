# ！/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019-2020 GDST <gdst.tw@gmail.com>

import json , requests ,random ,os,re,time
from lxml import etree
from opencc import OpenCC
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import gen as Gen
import get as Get
import sql

#Parameter
CHT_TW = True #優先取台灣譯名，且轉為繁體；若為False則為豆瓣上簡體中文標題
ZH_ENG = True #標題採中英混合；若為False則為僅中文標題 (當觸發ENGlen限制時則不保留英文標題)
regSt = True #地區縮寫，使用region.txt文件
Remote = True #將路徑替換為遠端路徑 (讀取掛載信息，但在遠端上操作)
remote = "16tn:" #承上，遠端路徑
Local = True #使用本地搜尋(gen.py)
LogPath = "D:\\AutoSortLog" #默認為執行目錄
LogName = "AutoSort"
SaveExcel = False #!未啟用
YearSort = True #老舊電影合併存放
Manual = 0 #0為全自動；1為遇到錯誤時切換為手動；2為自動搜尋手動確認 !未啟用
SearchMod = 0 #搜尋模式，0為使用原始資料夾名稱；1為 !未啟用
SubFolder = True #是否保留原始資料夾名稱，將其設為子資料夾 (當觸發pathlen限制時則不保留)
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

#SQL
db_name = "%s\\%s.db" % (LogPath,LogName) if LogPath else LogName+".db"
sql.init(db_name,"Movie")
sql.init(db_name,"TV")

with open("folder.txt" , "r", encoding = 'utf-8-sig') as data: #只在這些子資料夾執行
	folderList = [l.strip() for l in data ]
with open("region.txt" , "r", encoding = 'utf-8-sig') as regdata: #地區縮寫對應
	regList = [l.strip().split(',') for l in regdata ]
for reg in regList:
	regDic[reg[0]]=reg[1:]

#Function
def resjson(url):
    r = requests.get(url,headers={'User-Agent':ua.random})
    res = r.json() # return dict
    return res
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
		#LogName2 = "%s_Movie_%s.csv" % (LogName,year)
		LogName2 = "%s_Movie.tsv" % (LogName)
	elif subtype == "tv":
		#LogName2 = "%s_TV_%s_%s.csv" % (LogName,reg1,year)
		LogName2 = "%s_TV_%s.tsv" % (LogName,reg1)
	fname = LogPath+"\\"+LogName2
	if not os.path.isfile(fname):
		save = "年份\t地區\tIMDb\t豆瓣\t中文標題\t英文標題\t其他標題\t類型\tIMDb_id\tdb_id\tPath\n"+save
	with open(fname,"a", encoding = 'utf-8-sig') as sdata: #寫檔
		sdata.write(save+"\n")

class Search:
	def DB(key1,Manual=False): #Manual為手動整理參數 !暫未完成
		global subtype , dblink
		key2 = key1
		for i in range(len(key1),0,-1): #去除冗贅資料，以便查詢
			if i-1 > 0 and key1[i-4:i].isdigit() and key1[i-4:i] != "1080" and key1[i-4:i] != "2160":
				key2 = key1[:key1.find(key1[i-4:i])]
				if key2 != "":
					print("Change :",key2)
				else:
					key2 = key1
		Bracket = re.search(r"\[(.+?)\]",key2) #搜尋中括弧
		if Bracket:
			key2 = Bracket.group(1)
			print("Change :",key2)

		url = dbapi+key2
		res = resjson(url)
		if int(res['total']) == 1 and len(res['subjects'])==1: #Only 1 Result
			subtype = res['subjects'][0]['subtype']
			dblink = res['subjects'][0]['alt']
			year = res['subjects'][0]['year']
			if year in key1:
				return dblink
			else:
				print("*Error : Year doesn't match.")
		elif int(res['total']) == 0 or len(res['subjects'])==0: #找不到結果
			return ""
		elif int(res['total']) > 1 : #過多結果
			for subject in res['subjects']: #例外處理-過多資料-年份比對
				if subject['year'] in key1:
					subtype = subject['subtype']
					dblink = subject['alt']
					return dblink
			return False #Error : No results found.
	def GetInfo(dblink,switch=0):
		global year,subtype,reg1,reg2,reg3,save,genapinum
		if not Local:
			url2 = GenList[genapinum%3]+dblink
			try:
				r = requests.get(url2,headers={'User-Agent':ua.random},timeout=10)
			except requests.exceptions.ReadTimeout:
				print("*Error : Timeout")
				return ""
			if "Too Many Requests" in r.text:
				if switch < 3:
					switch += 1
					genapinum += 1
					print("*Error : Too Many Requests. Switch to another API.")
					Search.GetInfo(dblink,switch=switch)
				else:
					print("*Error : Too Many Requests. Wait for 300 seconds to retry")
					time.sleep(300)
					Search.GetInfo(dblink,switch=0)
				return
		res = r.json() if not Local else Gen.gen_douban(dblink)
		if not res['success']: # Success
			if res['error'] == "GenHelp was banned by Douban." and switch<3:
				print("*Error :",res['error'],"Switch to another API.")
				switch += 1
				genapinum += 1
				Search.GetInfo(dblink,switch=switch)
				return
			else:
				print("*Error :",res['error'])
				return ""
		else:
			year = res['year']
			if not year:
				year = res['playdate'][0][:4]
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
				breakcheck = False
				zhtwList = ["(台)","(港/台)","(台/港)","（台）","（港/台）","（台/港）"]
				for trans in AllTitle2:
					for zhtw in zhtwList:
						if zhtw in trans:
							if trans in AllTitle2:
								AllTitle2.remove(trans)
							breakcheck = True
							titleZH = trans.replace(zhtw,"")
							break
					if breakcheck:
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
					if not Get.checkzh(tt):
						if tt in AllTitle2:
							AllTitle2.remove(tt)
						titleEN = tt.replace(" : ","：").replace(": ","：")
						break
				for tt in [titleZH]+aka:
					if Get.checkzh(tt):
						if tt in AllTitle2:
							AllTitle2.remove(tt)
						titleZH = tt.replace(" : ","：").replace(": ","：")
						break
				title = (titleZH+" "+titleEN) if titleEN and len(titleEN) <= ENGlen else titleZH
			titleOT = AllTitle2

			region = reg2 if regSt else reg1
			titleOT = [] if not titleOT else titleOT
			save = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (mvid,year,reg1,imdb_rating,db_rating,titleZH,titleEN,"／".join(titleOT),genre,imdb_id,db_id)
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

mypath = os.getcwd() if not Remote else remote #執行目錄
Logfile = LogPath+"\\move.log" if LogPath else "move.log"

for folder in folderList:
	if os.path.isdir(folder): #如果指定的資料夾存在
		for d in os.listdir(folder):
			subtype,IMDbID = "",""
			folderpath = "%s/%s" % (folder,d)
			print("\nFolder :",d)

			if re.search(r"\(db_(.+?)\)",d): #如果能從資料夾名稱找到dbID
				dblink = "https://movie.douban.com/subject/%s/" % (re.search(r"\(db_(.+?)\)",d).group(1))
			elif re.search(r"\(tt(.+?)\)",d): #如果能從資料夾名稱找到IMDbID
				IMDbID = re.search(r"\((tt\d+)\)",d).group(1)
				print("IMDbID :",IMDbID)
				dblink = Get.imdb2db(IMDbID)
			elif Get.findnfo(folderpath): #如果能從資料夾內的.nfo找到IMDb或douban鏈接
				get_nfo = Get.findnfo(folderpath)
				if 'imdb' in get_nfo.keys():
					IMDbID = get_nfo['imdb']
					print("IMDbID :",IMDbID)
					dblink = Get.imdb2db(get_nfo['imdb'])
				elif 'douban' in get_nfo.keys():
					dblink = get_nfo['douban']
			else:
				dblink = Search.DB(d)
			if dblink: #如果能返回豆瓣鏈接
				name = Search.GetInfo(dblink)
				if not name and IMDbID: #如果無法從dblink找到資料，但存在IMDbID
					GetTMDb = Get.IMDb2TMDb(IMDbID)
					if GetTMDb:
						subtype,year,reg1,name,save = GetTMDb[0],GetTMDb[1],GetTMDb[2],GetTMDb[3],GetTMDb[4]
						print("Change : IMDb&TMDb")
					else:
						subtype,year,reg1,name,save = "","","","",""
			elif not dblink and IMDbID: #如果無法返回dbLink，但有IMDbID→改用TMDB跟IMDb搜尋資訊
				GetTMDb = Get.IMDb2TMDb(IMDbID)
				if GetTMDb:
					subtype,year,reg1,name,save = GetTMDb[0],GetTMDb[1],GetTMDb[2],GetTMDb[3],GetTMDb[4]
					print("Change : IMDb&TMDb")
				else:
					subtype,year,reg1,name,save = "","","","",""
			else:
				print("*Error : Can't find dbLink.")
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
				table_name = "Movie"
				Path = ("Movie\\%s\\%s" % (year,name))
			elif subtype == "tv":
				table_name = "TV"
				Path = ("TVSeries\\%s\\%s\\%s" % (reg1,year,name))
			path1 = mypath+"\\"+folder+"\\"+d
			path2 = mypath+"\\"+Path+"\\"+d if SubFolder or subtype == "tv" else mypath+"\\"+Path
			if len(path2) > pathlen and not subtype == "tv" : #路徑長度(但對TV類型不啟用)
				path2 = mypath+"\\"+Path
			#command = ("rclone move -v \"%s\" \"%s\"" %(path1,path2))
			command = ("rclone move -v \"%s\" \"%s\" --log-file=%s" %(path1,path2,Logfile))
			command2 = ("rclone move -v \"%s\" \"%s\" --log-file=%s" %(path1,path2,Logfile))
			#os.popen(command)
			os.system(command)
			print("MoveTo :",path2)
			if IMDbID:
				SaveLog("%s\t%s\t%s" % (save,IMDbID,Path))
			else:
				SaveLog("%s\t%s\t%s" % (save,d,Path))
			sql.input(db_name, table_name, save.split("\t")+[Path])
