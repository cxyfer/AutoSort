# coding: utf-8
#v2.0 20180929
##增加檔案比對、自動重新命名
#v3.0 20180930
##增加批次處理，將欲處理的番號存在keylist.txt
#v3.1 20181006
##更新運算邏輯、重新整理架構、新增素人片番號的比對及封面下載、
##比對檔案改為直接比對檔案大小、以及些許細部調整

import os , requests , urllib , time ,filecmp ,hashlib
from bs4 import BeautifulSoup

CheckFile = True #是否進行重複檔案杜對

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
def hashs(fineName, type="md5", block_size=128 * 1024):
	""" Support md5(), sha1(), sha224(), sha256(), sha384(), sha512(), blake2b(), blake2s(),
	sha3_224, sha3_256, sha3_384, sha3_512, shake_128, and shake_256
	"""
	with open(fineName, 'rb') as file:
		hash = hashlib.new(type, b"")
		while True:
			data = file.read(block_size)
			if not data:
				break
			hash.update(data)
		return hash.hexdigest()

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
	def Cover1(code):
		global title , dirpath ,imglink
		url = "https://www.javbus.com/"+code
		response = requests.get(url)
		response.encoding = 'UTF-8' 
		soup = BeautifulSoup(response.text, 'lxml')

		if soup.find("title").getText() == "404 Not Found" or soup.find("title").getText() == "404 Page Not Found! - JavBus":
			text = "*Error : " + code+ " 404 Not Found"
			textpath = "Path : "+root 
			Log.Text(textpath)
			Log.NPrint(text)
			return
		elif soup.find("h3") == None:
			Log.NPrint("*Error : " + code+ " Unknown Error")
			textpath = "Path : "+root 
			Log.Text(textpath)
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

		if os.path.isdir(mypath+"\\@~Sorted\\"+key+"\\"+title):
			dirpath = mypath+"\\@~Sorted\\"+key+"\\"+title
		elif os.path.isdir(mypath+"\\@~Sorted\\"+key+"\\"+code):
			dirpath = mypath+"\\@~Sorted\\"+key+"\\"+code
		else:	
			try:
				os.mkdir(mypath+"\\@~Sorted\\"+key+"\\"+title)
				dirpath = mypath+"\\@~Sorted\\"+key+"\\"+title
			except:
				os.mkdir(mypath+"\\@~Sorted\\"+key+"\\"+code)
				dirpath = mypath+"\\@~Sorted\\"+key+"\\"+code
		os.chdir(dirpath)
		if not os.path.isfile(filename) or os.stat(filename).st_size == 0:
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

	def Cover2(code):
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
			textpath = "Path : "+root 
			Log.Text(textpath)
			Log.NPrint(text)

		imgs = soup.find_all("div","col-xs-12 col-md-12")[:-1]
		imglist = [i.find("img").get("src") for i in imgs]
		imglink = imglist[0]

		if os.path.isdir(mypath+"\\@~Sorted\\"+key+"\\"+title):
			dirpath = mypath+"\\@~Sorted\\"+key+"\\"+title
		elif os.path.isdir(mypath+"\\@~Sorted\\"+key+"\\"+code):
			dirpath = mypath+"\\@~Sorted\\"+key+"\\"+code
		else:	
			try:
				os.mkdir(mypath+"\\@~Sorted\\"+key+"\\"+title)
				dirpath = mypath+"\\@~Sorted\\"+key+"\\"+title
			except:
				os.mkdir(mypath+"\\@~Sorted\\"+key+"\\"+code)
				dirpath = mypath+"\\@~Sorted\\"+key+"\\"+code
		os.chdir(dirpath)
		print("StartDL : "+code)
		for img in imglist:
			dotpos = img.rfind("/")
			filename = img[dotpos+1:]

			r = requests.get(img)
			if not os.path.isfile(filename) or os.stat(filename).st_size == 0:
				try:
					with open(filename, "wb") as imgdata:
						imgdata.write(r.content)
				except:
					try:
						with open(code+".jpg", "wb") as imgdata:
							imgdata.write(r.content)
					except:
						return
		print("CoverDL : "+title)
		return True

	def DL(key):
		r = requests.get(imglink)
		filename = title + ".jpg"
		os.chdir(mypath+"\\@~Sorted\\"+key)
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
	if mypath+"\\@~Sorted" in root or mypath+"\\@" in root or "新作" in root or "合集" in root : #略過根目錄下帶有@的資料夾 (特製)
		continue
	if not os.path.isdir(mypath+"\\@~Sorted\\"):
		os.mkdir(mypath+"\\@~Sorted\\")
	os.chdir(root) #更改到當前目錄
	print("\nPath : "+root)
	
	for key in KeyList:
		for i in files:
			dirpath = mypath
			code = GetCode(i) #從檔名找番號
			if code : #如果能夠從檔案名稱找出番號
				print("Code :",code)
				if not os.path.isdir(mypath+"\\@~Sorted\\"+key):
					os.mkdir(mypath+"\\@~Sorted\\"+key)
				x = DL.Cover1(code) if not key[0].isdigit() or not key =="SIRO" else DL.Cover2(code)
				if x : #如果存在對應的資料，且下載封面成功
					print("File : "+i)
					DL.DL(key)
				else:
					continue

				fsize = file_size(root+"\\"+i).split(" ") #檢查檔案大小，改檔名
				if fsize[1] == "GB" and float(fsize[0]) >= 4 and ("HD" not in i):
					dotpos = i.rfind(".")
					i2 = i[:dotpos]+".HD"+i[dotpos:]
					print("Rename : "+i2)
				else:
					i2=i
				if not os.path.isfile(dirpath+"\\"+i2): #若檔案不存在
					os.rename(root+"\\"+i,dirpath+"\\"+i2)
					print("Move : "+dirpath)
				else: #若檔案存在
					file1 = root+"\\"+i
					file2 = dirpath+"\\"+i2
					if CheckFile and file_size(file1) == file_size(file2) : #若需要比對檔案，且存在的檔案相同
					#if CheckFile and file_size(file1) == file_size(file2) and hashs(file1) == hashs(file2) : #若需要比對檔案，且存在的檔案相同
						Log.NPrint("*Error : Exist same file \n  *FileName : "+i+"\n  *FilePath : "+root)
					else: #若存在的檔案不同
						for j in range(1,10):
							dotpos = i2.rfind(".")
							i3 = i2[:dotpos]+"~"+str(j)+i2[dotpos:]
							if not os.path.isfile(dirpath+"\\"+i3):
								os.rename(root+"\\"+i,dirpath+"\\"+i3)
								Log.NPrint("*Exist : "+i+"\n *Rename : "+i3)
								print("Move : "+dirpath)
								break
				Log.SaveList(key,True)
				Log.SaveList(key,False)
input("\n整理完成，請按Enter離開")