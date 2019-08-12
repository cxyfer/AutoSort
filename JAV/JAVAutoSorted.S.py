#-*- coding: utf-8 -*-
#v4.0 20190710
##重新整理函數，加入預覽圖下載合併
import os, requests, urllib, time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import config

ua = UserAgent()

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
	#if key == "IBW" or key == "AOZ" : #IBW特製
	#	code += "Z"
	return code

#要處理的番號清單
with open("keyword.txt" , "r", encoding = 'utf-8-sig') as keydata: 
	KeyList = [l.strip() for l in keydata ]
with open("keyword2.txt" , "r", encoding = 'utf-8-sig') as keydata: #找不到資料庫的特殊番號(備用)
	Key2List = [l.strip().split(",") for l in keydata ]
Key2Dic = {}
for i in Key2List:
	Key2Dic[i[0]]=i[1]

mypath = os.getcwd() #執行目錄
for lsdir in sorted(os.listdir(mypath)):
	if not os.path.isdir(mypath+"\\"+lsdir): #如果不是資料夾
		continue
	if lsdir[0]=="@" or "新作" in lsdir or "合集" in lsdir: #略過根目錄下帶有@的資料夾 (特製)
		continue
	if not os.path.isdir(mypath+"\\@~Sorted\\"):
		os.mkdir(mypath+"\\@~Sorted\\")
	for root, dirs, files in os.walk(mypath+"\\"+lsdir):
		#os.chdir(root) #更改到當前目錄
		print("\nPath : "+root)
		for i in files:
			for key2 in Key2Dic.keys(): #!待新增，對於無資料庫的番號進行處理
				key2 = key2
			for key in KeyList:
				if "padding_file" in i or "HstarForum" in i: #去除容易誤判的冗贅檔案名
					continue
				dirpath = mypath
				code = GetCode(i) #從檔名找番號
				if code : #如果能夠從檔案名稱找出番號
					#if key == "336KNB" or key == "302GERK": #臨時處理
					#	continue
					print("Code :",code)
					if not os.path.isdir(mypath+"\\@~Sorted\\"+key):
						os.mkdir(mypath+"\\@~Sorted\\"+key)
					x = DL.Cover2(code) if key[0].isdigit() or key =="SIRO" or key =="KIRAY" else DL.Cover1(code)
					#x = DL.Cover2(code)
					if x : #如果存在對應的資料，且下載封面成功
						print("File : "+i)
						DL.DL(key)
					else:
						code = code.replace("-00","-") #例外處理：部分番號會用5位數字，但搜尋時必須為3位
						print("Code :",code)
						#x2 = DL.Cover2(code) if key[0].isdigit() or key =="SIRO" else DL.Cover1(code)
						x2 = DL.Cover2(code)
						if x2 :
							print("File : "+i)
							DL.DL(key)
						else:
							continue
					'''fsize = file_size(root+"\\"+i).split(" ") #檢查檔案大小，改檔名
					if fsize[1] == "GB" and float(fsize[0]) >= 4 and ("HD" not in i):
						dotpos = i.rfind(".")
						i2 = i[:dotpos]+".HD"+i[dotpos:]
						print("Rename : "+i2)
					else:
						i2=i'''
					i2=i
					if not os.path.isfile(dirpath+"\\"+i2): #若檔案不存在
						os.rename(root+"\\"+i,dirpath+"\\"+i2)
						print("Move : "+dirpath)
					else: #若檔案存在
						file1 = root+"\\"+i
						file2 = dirpath+"\\"+i2
						if config.CheckFile and file_size(file1) == file_size(file2) : #若需要比對檔案，且存在的檔案相同
						#if config.CheckFile and file_size(file1) == file_size(file2) and hashs(file1) == hashs(file2) : #若需要比對檔案，且存在的檔案相同
							os.remove(file1)
							Log.NPrint("*Error : Exist same file \n  *Remove : "+file1)
						else: #若存在的檔案不同
							for j in range(1,10):
								dotpos = i2.rfind(".")
								i3 = i2[:dotpos]+"~"+str(j)+i2[dotpos:]
								if not os.path.isfile(dirpath+"\\"+i3):
									try:
										os.rename(root+"\\"+i,dirpath+"\\"+i3)
									except FileNotFoundError:
										Log.NPrint("*Error : FileNotFound "+file1)
										break
									Log.NPrint("*Exist : "+i+"\n *Rename : "+i3)
									print("Move : "+dirpath)
									break
					Log.SaveList(key,True)
					Log.SaveList(key,False)
input("\n整理完成，請按Enter離開")