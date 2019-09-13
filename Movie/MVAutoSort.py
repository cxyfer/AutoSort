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
import sql,search,config

#Initialize
ua = UserAgent()
regDic = {}

#SQL
db_name = "%s\\%s.db" % (config.LogPath,config.LogName) if config.LogPath else config.LogName+".db"
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
		#config.LogName2 = "%s_Movie_%s.csv" % (config.LogName,year)
		config.LogName2 = "%s_Movie.tsv" % (config.LogName)
	elif subtype == "tv":
		#config.LogName2 = "%s_TV_%s_%s.csv" % (config.LogName,reg1,year)
		config.LogName2 = "%s_TV_%s.tsv" % (config.LogName,reg1)
	fname = config.LogPath+"\\"+config.LogName2
	if not os.path.isfile(fname):
		save = "Folder\tSID\tRename\n"+save
	with open(fname,"a", encoding = 'utf-8-sig') as sdata: #寫檔
		sdata.write(save+"\n")
def LogNPrint(text):
	print(text)
	with open(config.LogPath+"//AutoSort.log","a", encoding = 'utf8') as data:
		data.write(str(text)+"\n")

class Search:
	def DB(key1):
		global subtype , dblink
		key2,year0 = key1,""
		digit4 = re.findall(r"\d{4}",key2)
		for dig4 in digit4: #去除冗贅資料，以便查詢
			if dig4 != "1080" and dig4 != "2160":
				year0 = dig4
				key2 = key1[:key1.find(dig4)] if key1[:key1.find(dig4)] != "" else key1 
				break
			else:
				key2 = key1[:key1.find(dig4)] if key1[:key1.find(dig4)] != "" else key1
		print("Change :",key2)
		Bracket = re.search(r"\[(.+?)\]",key2) #搜尋中括弧
		if Bracket:
			key2 = Bracket.group(1)
			print("Change :",key2)
		url = config.dbapi+key2
		res = resjson(url)
		if int(res['total']) == 1 and len(res['subjects'])==1: #Only 1 Result
			subtype = res['subjects'][0]['subtype']
			dblink = res['subjects'][0]['alt']
			year = res['subjects'][0]['year']
			if year in key1 or not year0:
				return dblink
			else:
				print("*Error : Year doesn't match.")
		elif int(res['total']) == 0 or len(res['subjects'])==0: #找不到結果trf
			return ""
		elif int(res['total']) > 1 : #過多結果
			for subject in res['subjects']: #例外處理-過多資料-年份比對
				if subject['year'] in key1:
				#if subject['year'] in key1 or (not year0 and subject['title'] in key1):
					subtype = subject['subtype']
					dblink = subject['alt']
					return dblink
			return False #Error : No results found.
	def GetInfo(dblink,switch=0):
		global year,subtype,reg1,reg2,reg3,save
		res = Gen.gen_douban(dblink)
		if not res['success']: # Success
			print("*Error :",res['error'])
			return ""
		else:
			if not subtype:
				subtype = "tv" if res['episodes'] else "movie"
			year = year2 = res['year']
			if not year:
				print(res['playdate'])
				year = res['playdate'][0][:4]
			'''if int(len(res['seasons_list'])) > 1 and subtype == "tv": #多季的電視劇
				year = 999 #多季
				year2 = "多季"'''
			titleZH = res['chinese_title'] #中文標題
			this_title = res['this_title'][0] #原始標題
			trans_title = res['trans_title'] #List 用來取台灣譯名
			aka = res['aka']

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
					reg1 = reg.replace("中国","") if "台湾" in region or "香港" in region else reg
					reg2 = regDic[reg][0]
					reg3 = regDic[reg][1]
					break

			AllTitle1 = [titleZH]+[this_title]+aka+trans_title
			AllTitle2 = list(set(AllTitle1))
			AllTitle2.sort(key=AllTitle1.index)

			if config.CHT_TW: #繁體、台灣譯名
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
			if config.ZH_ENG: #中英標題
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
				title = (titleZH+" "+titleEN) if titleEN and len(titleEN) <= config.ENGlen and titleZH != titleEN else titleZH
			titleOT = AllTitle2

			region = reg2 if config.regSt else reg1
			titleOT = [] if not titleOT else titleOT
			save = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (mvid,year,reg1,imdb_rating,db_rating,titleZH,titleEN,"／".join(titleOT),genre,imdb_id,db_id)
			if float(rating):
				return "[%s][%s]%s(%s)(%s)(%s)" % (year2,region,title,genre.replace("|","_"),rating,mvid)
			else:
				return "[%s][%s]%s(%s)(%s)" % (year2,region,title,genre.replace("|","_"),mvid)

mypath = os.getcwd() if not config.UseRemote else config.remotepath #執行目錄
Logfile = config.LogPath+"\\move.log" if config.LogPath else "move.log"

for folder in folderList:
	if os.path.isdir(folder): #如果指定的資料夾存在
		for d in sorted(os.listdir(folder)):
			subtype,IMDbID,dblink= "","",""
			folderpath = "%s/%s" % (folder,d)
			SubD = False if re.match(r'.+?\.(mkv|mp4|ts)', d) else config.SubFolder #若資料夾為檔案名稱，則不使用config.SubFolder
			LogNPrint("\nFolder : "+d)
			if re.search(r"\(db_(.+?)\)",d): #如果能從資料夾名稱找到dbID
				SubD = False
				dblink = "https://movie.douban.com/subject/%s/" % (re.search(r"\(db_(.+?)\)",d).group(1))
			elif re.search(r"\(tt(.+?)\)",d): #如果能從資料夾名稱找到IMDbID
				SubD = False
				IMDbID = re.search(r"\((tt\d+)\)",d).group(1)
				LogNPrint("IMDbID : "+IMDbID)
				dblink = Get.imdb2db(IMDbID)
			elif Get.findnfo(folderpath): #如果能從資料夾內的.nfo找到IMDb或douban鏈接
				get_nfo = Get.findnfo(folderpath)
				if 'imdb' in get_nfo.keys():
					IMDbID = get_nfo['imdb']
					LogNPrint("IMDbID : "+IMDbID)
					dblink = Get.imdb2db(get_nfo['imdb'])
				elif 'douban' in get_nfo.keys():
					dblink = get_nfo['douban']
			elif re.search(r"(Aka|Ao|FLTTH|iLoveHD|iLoveTV|MGs|OurPad|OurTV|PbK)",d) and search.ourbits(d): #如果能從Ourbits找到IMDbID或dblink
				ptsearch = search.ourbits(d)
				LogNPrint("Search : from Ourbits")
				IMDbID = ptsearch['imdb'] if ptsearch['imdb'] else ""
				dblink = ptsearch['douban'] if ptsearch['douban'] else Get.imdb2db(IMDbID)
			elif re.search(r"CMCT",d) and search.SSD(d): #如果能從SSD找到IMDbID或dblink
				ptsearch = search.SSD(d)
				LogNPrint("Search : from SSD")
				IMDbID = ptsearch['imdb'] if ptsearch['imdb'] else ""
				dblink = ptsearch['douban'] if ptsearch['douban'] else Get.imdb2db(IMDbID)
			elif re.search(r"TJUPT",d) and search.TJUPT(d): #如果能從TJUPT找到IMDbID或dblink
				ptsearch = search.TJUPT(d)
				LogNPrint("Search : from TJUPT")
				IMDbID = ptsearch['imdb'] if ptsearch['imdb'] else ""
				dblink = ptsearch['douban'] if ptsearch['douban'] else Get.imdb2db(IMDbID)
			elif re.search(r"FRDS",d) and search.FRDS(d): #如果能從FRDS找到IMDbID或dblink
				ptsearch = search.FRDS(d)
				LogNPrint("Search : from FRDS")
				IMDbID = ptsearch['imdb'] if ptsearch['imdb'] else ""
				dblink = ptsearch['douban'] if ptsearch['douban'] else Get.imdb2db(IMDbID)
			elif re.search(r"PuTao",d) and search.PuTao(d): #如果能從PuTao找到IMDbID或dblink
				ptsearch = search.PuTao(d)
				LogNPrint("Search : from PuTao")
				IMDbID = ptsearch['imdb'] if ptsearch['imdb'] else ""
				dblink = ptsearch['douban'] if ptsearch['douban'] else Get.imdb2db(IMDbID)
			else:
				dblink = Search.DB(d)
			if dblink: #如果能返回豆瓣鏈接
				LogNPrint("dbLink : "+dblink)
				name = Search.GetInfo(dblink)
				if not name and IMDbID: #如果無法從dblink找到資料，但存在IMDbID
					GetTMDb = Get.IMDb2TMDb(IMDbID)
					if GetTMDb:
						subtype,year,reg1,name,save = GetTMDb[0],GetTMDb[1],GetTMDb[2],GetTMDb[3],GetTMDb[4]
						LogNPrint("Change : IMDb&TMDb")
					else:
						subtype,year,reg1,name,save = "","","","",""
			elif not dblink and IMDbID: #如果無法返回dbLink，但有IMDbID→改用TMDB跟IMDb搜尋資訊
				GetTMDb = Get.IMDb2TMDb(IMDbID)
				if GetTMDb:
					subtype,year,reg1,name,save = GetTMDb[0],GetTMDb[1],GetTMDb[2],GetTMDb[3],GetTMDb[4]
					LogNPrint("Change : IMDb&TMDb")
				else:
					LogNPrint("*Error : Can't find info from IMDb&TMDb.")
					subtype,year,reg1,name,save = "","","","",""
			else:
				LogNPrint("*Error : Can't find dbLink.")
				continue

			if name:
				name = name.replace("\"","")
				LogNPrint("Subtype: "+subtype)
			else:
				continue
			if config.YearSort:
				if int(year) > 2000:
					year = year
				#elif int(year) == 999:
				#	year = "多季"
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

			query = sql.query(db_name, table_name,save.split("\t")[0]) #查詢舊有資料
			if query != None and not config.DataUpdate: #若存在舊有資料且不須更新現有資料
				Path = query[-1]
				name = Path[Path.rfind("\\")+1:]
			elif query != None and config.DataUpdate: #若存在舊有資料且與新的資料不相符(數據更新)且更新資料參數為True
				sql.input(db_name, table_name, save.split("\t")+[Path],replace=True)
				command2 = ("rclone move -v \"%s\" \"%s\" --log-file=%s" %(mypath+"\\"+query[-1],mypath+"\\"+Path,Logfile))
				os.system(command2)
			else: #資料庫內無對應資料
				sql.input(db_name, table_name, save.split("\t")+[Path])

			LogNPrint("Rename : "+name)
			path1 = mypath+"\\"+folder+"\\"+d
			path2 = mypath+"\\"+Path+"\\"+d if SubD or subtype == "tv" else mypath+"\\"+Path
			if len(path2) > config.pathlen and not subtype == "tv" : #路徑長度(但對TV類型不啟用)
				path2 = mypath+"\\"+Path
			command = ("rclone move -v \"%s\" \"%s\" --log-file=%s" %(path1,path2,Logfile))
			os.system(command)
			LogNPrint("MoveTo : "+path2)
		command = ("rclone rmdirs -v \"%s\"" % (mypath+"\\"+folder))
		os.system(command)