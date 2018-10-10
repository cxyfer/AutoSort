# coding: utf-8
#v2.0
##增加檔案比對、自動重新命名
#v3.0
##預計增加批次處理，將欲處理的番號存在keylist.txt
import os , requests , urllib , time ,filecmp ,hashlib
from bs4 import BeautifulSoup

DLRoot = True
DLSeparately = False

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

		os.chdir(mypath)
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
	if key == "IBW" : #IBW特製
		code += "Z"
	return code

class DL:
	def Cover1(code,Check):
		global title , dirpath ,imglink
		url = "https://www.javbus.com/"+code
		response = requests.get(url)
		response.encoding = 'UTF-8' 
		soup = BeautifulSoup(response.text, 'lxml')

		if soup.find("title").getText() == "404 Not Found" or soup.find("title").getText() == "404 Page Not Found! - JavBus":
			text = "*Error : " + code+ " 404 Not Found"
			Log.NPrint(text)
			return
		elif soup.find("h3") == None:
			Log.NPrint("*Error : " + code+ " Unknown Error")
			Log.Text(str(soup))
			return
		
		article = soup.find("div", {"class": "container"})
		if article == None:
			Log.NPrint("*Error : " + code+ " Unknown Error")
			return
		title = article.find("h3").getText()
		imglink = article.find("a", {"class": "bigImage"}).get("href")

		r = requests.get(imglink)
		filename = title + ".jpg"

		if Check :
			return True
		dirpath = root
		os.chdir(dirpath)
		if not os.path.isfile(filename):
			try:
				with open(filename, "wb") as imgdata:
					imgdata.write(r.content)
				print("CoverDL : "+title)
				return True
			except:
				with open(code+".jpg", "wb") as imgdata:
					imgdata.write(r.content)
				print("CoverDL : "+title)
				return True
		else:
			return True

	def Cover2(code,Check):
		global title , dirpath ,imglink
		url = "https://www.jav321.com/video/"+code
		response = requests.get(url)
		response.encoding = 'UTF-8' 
		soup = BeautifulSoup(response.text, 'lxml')

		t1 = soup.find("h3").getText()
		t2 = soup.find("h3").find("small").getText()
		title = code + " " +t1.replace(t2,"").strip()

		if  t1.replace(t2,"") == " ":
			text = "*Error : " + code+ " 404 Not Found"
			Log.NPrint(text)

		imgs = soup.find_all("div","col-xs-12 col-md-12")[:-1]
		imglist = [i.find("img").get("src") for i in imgs]
		imglink = imglist[0]


		if Check :
			return True
		dirpath = root
		filename = title + ".jpg"
		os.chdir(dirpath)
		r = requests.get(imglink)
		if not os.path.isfile(filename):
			try:
				with open(filename, "wb") as imgdata:
					imgdata.write(r.content)
				print("CoverDL : "+title)
				return True
			except:
				with open(code+".jpg", "wb") as imgdata:
					imgdata.write(r.content)
				print("CoverDL : "+title)
				return True
		else:
			return True

	def DL():
		r = requests.get(imglink)
		filename = title + ".jpg"
		os.chdir(mypath)
		if not os.path.isfile(filename):
			try:
				with open(filename, "wb") as imgdata:
					imgdata.write(r.content)
			except:
				with open(code+".jpg", "wb") as imgdata:
					imgdata.write(r.content)

#要處理的番號清單
with open("keyword.txt" , "r", encoding = 'utf8') as keydata: 
	KeyList = [l.strip() for l in keydata ]

mypath = os.getcwd() #執行目錄

for root, dirs, files in os.walk(mypath):
	os.chdir(root) #更改到當前目錄
	print("Path : "+root+"\n")
	
	for key in KeyList:
		for i in files:
			dirpath = mypath
			code = GetCode(i) #從檔名找番號
			if code : #如果能夠從檔案名稱找出番號
				x = DL.Cover1(code,DLSeparately) if not key[0].isdigit() else DL.Cover2(code,DLSeparately)
				if x : #如果存在對應的資料，且下載封面成功
					print("File : "+i)
					DL.DL()
				else:
					continue
				Log.SaveList(key,True)
				Log.SaveList(key,False)
input("\n整理完成，請按Enter離開")