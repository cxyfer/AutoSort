#-*- coding: utf-8 -*-
#v4.0 20190710
##重新整理函數、加入預覽圖下載合併
#v4.2 20190807-(未完成)
##資料庫輸出、相同檔案去重(檢查檔案大小)

import os, requests, urllib, time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import config, search, sql

ua = UserAgent()
db_name = "%s\\%s" % (config.LogPath,config.LogName) if config.LogPath else config.LogName #SQL

class Log:
	def NPrint(text):
		os.chdir(mypath)
		print(text)
		with open("error.log","a", encoding = 'utf8') as data:
			data.write(str(text)+"\n")
	def Text(text):
		with open("error.log","a", encoding = 'utf8') as data:
			data.write(str(text)+"\n")
	def SaveList(key,Title):
		fname = ("@FileList.txt" if Title else "@CodeList.txt")
		new = (title if Title else code)

		os.chdir(mypath+"\\@~Sorted\\"+key)
		try: #讀取先前的清單
			with open(fname , "r", encoding = 'utf8') as clog: 
				SaveList = [l.strip() for l in clog ]
		except:
			SaveList = []
		if new not in SaveList :
			SaveList += [new]
		else:
			return
		if len(SaveList) != 0: #如果非空目錄的話
			with open(fname,"w", encoding = 'utf8') as sdata: #寫檔
				for i in sorted(SaveList):
					sdata.write(i+"\n")
def convert_bytes(num):
	for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
		if num < 1024.0:
			return "%3.1f %s" % (num, x)
		num /= 1024.0
def file_size(file_path):
	if os.path.isfile(file_path):
		file_info = os.stat(file_path)
		return convert_bytes(file_info.st_size)
def GetCode(filename):
	c = key.upper()+"-"
	if c in filename.upper():
		cpos = filename.upper().find(c)
	elif key.upper() in filename.upper():
		c = key.upper()
		cpos = filename.upper().find(c)
		filename = filename.upper().replace(c,c+"-")
		c = c+"-"
	else:
		return None
	for i in range(len(filename[cpos+len(c):])):
		if not filename[cpos+len(c)+i].isdigit():
			code = filename[cpos:cpos+len(c)+i]
			code = code.upper()
			break
	if len(code) == len(c) : #如果找不到番號(番號跟關鍵字長度一樣)
		return None
	return code

#要處理的番號清單
with open("keyword.txt" , "r", encoding = 'utf-8-sig') as keydata: 
	KeyList = [l.strip() for l in keydata]
KeyList = list(set(KeyList)) #番號去重
if not os.path.isdir(config.tempfolder): #如果不是資料夾
	os.mkdir(config.tempfolder)

'''with open("keyword2.txt" , "r", encoding = 'utf-8-sig') as keydata: #找不到資料庫的特殊番號 (!待新增)
	Key2List = [l.strip().split(",") for l in keydata ]
Key2Dic = {}
for i in Key2List:
	Key2Dic[i[0]]=i[1]'''

mypath = os.getcwd() #執行目錄
for lsdir in sorted(os.listdir(mypath)):
	if not os.path.isdir(mypath+"\\"+lsdir): #如果不是資料夾
		continue
	if lsdir[0]=="@" or lsdir == "__pycache__" or "新作" in lsdir or "合集" in lsdir: #略過根目錄下帶有@的資料夾 (個人化)
		continue
	if not os.path.isdir(mypath+"\\@~Sorted\\"):
		os.mkdir(mypath+"\\@~Sorted\\")
	for root, dirs, files in os.walk(mypath+"\\"+lsdir):
		print("\nPath : "+root)
		for i in files:
			'''for key2 in Key2Dic.keys(): #對於無資料庫的番號進行處理 (!待新增)
				key2 = key2'''
			for key in KeyList:
				if "padding_file" in i: #去除容易誤判的冗贅檔案名
					continue
				dirpath = mypath
				code = GetCode(i) #從檔名找番號
				if not code : #如果不能夠從檔案名稱找出番號
					continue
				if len(code[code.find("-")+1:]) >= 5: #例外處理：部分番號會用5位數字，但搜尋時必須為3位
					code = code.replace("-00","-") 
				print("Code :",code)
				if not os.path.isdir(mypath+"\\@~Sorted\\"+key):
					os.mkdir(mypath+"\\@~Sorted\\"+key)
				result = search.Database2(key,code,mypath) if key[0].isdigit() or key =="SIRO" or key =="KIRAY" else search.Database1(key,code,mypath)
				if not result['success']: #如果不存在對應的資料
					result = search.Database1(key,code,mypath) if key[0].isdigit() or key =="SIRO" or key =="KIRAY" else search.Database2(key,code,mypath) #調換
					if not result['success']:
						continue
				save = result['save']
				print("File : "+i)
				i2=i #檔案移動處理
				dirpath = result['dirpath']
				if not os.path.isfile(dirpath+"\\"+i2): #若檔案不存在
					os.rename(root+"\\"+i,dirpath+"\\"+i2)
					print("Move : "+dirpath)
				else: #若檔案存在
					file1 = root+"\\"+i
					file2 = dirpath+"\\"+i2
					if config.CheckFile and file_size(file1) == file_size(file2) : #若需要比對檔案，且存在的檔案相同
						os.remove(file1)
						print("*Error : Exist same file \n  *Remove : "+file1)
					else: #若存在的檔案不同
						for j in range(1,10):
							dotpos = i2.rfind(".")
							i3 = i2[:dotpos]+"~"+str(j)+i2[dotpos:]
							if not os.path.isfile(dirpath+"\\"+i3):
								try:
									os.rename(root+"\\"+i,dirpath+"\\"+i3)
								except FileNotFoundError:
									print("*Error : FileNotFound "+file1)
									break
								print("*Exist : "+i+"\n *Rename : "+i3)
								print("Move : "+dirpath)
								break
				sql.input(db_name,'JAV', save)
input("\n整理完成，請按Enter離開")