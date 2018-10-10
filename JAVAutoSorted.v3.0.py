# coding: utf-8
#v2.0
##增加檔案比對、自動重新命名
#v3.0
##預計增加批次處理，將欲處理的番號存在keylist.txt
import os , requests , urllib , time ,filecmp ,hashlib
from bs4 import BeautifulSoup

def logNprint(text):
	os.chdir(mypath)
	print(text)
	with open("error.log","a", encoding = 'utf8') as data:
		data.write(str(text)+"\n")
def log(text):
	with open("error.log","a", encoding = 'utf8') as data:
		data.write(str(text)+"\n")
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

	return code

def CoverDL(code,dlornot):
	global TitleList , dirpath
	url = "https://www.javbus.com/"+code
	response = requests.get(url)
	response.encoding = 'UTF-8' 
	soup = BeautifulSoup(response.text, 'lxml')

	if soup.find("title").getText() == "404 Not Found" or soup.find("title").getText() == "404 Page Not Found! - JavBus": #404檢查
		text = "*Error : " + code+ " 404 Not Found"
		logNprint(text)
		return
	elif soup.find("h3") == None:
		logNprint("*Error : " + code+ " Unknown Error")
		log(str(soup))
		return
		
	article = soup.find("div", {"class": "container"})
	if article == None:
		logNprint("*Error : " + code+ " Unknown Error")
		return
	title = article.find("h3").getText()
	imglink = article.find("a", {"class": "bigImage"}).get("href")
	TitleList += [title]

	r = requests.get(imglink)
	filename = title + ".jpg"

	if os.path.isdir(mypath+"\\@Sorted\\"+key+"\\"+title):
		dirpath = mypath+"\\@Sorted\\"+key+"\\"+title
	elif os.path.isdir(mypath+"\\@Sorted\\"+key+"\\"+code):
		dirpath = mypath+"\\@Sorted\\"+key+"\\"+code
	else:	
		try:
			os.mkdir(mypath+"\\@Sorted\\"+key+"\\"+title)
			dirpath = mypath+"\\@Sorted\\"+key+"\\"+title
		except:
			os.mkdir(mypath+"\\@Sorted\\"+key+"\\"+code)
			dirpath = mypath+"\\@Sorted\\"+key+"\\"+code
	os.chdir(dirpath)
	if dlornot:
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


#要處理的番號清單
with open("keyword.txt" , "r", encoding = 'utf8') as keydata: 
	KeyList = [l.strip() for l in keydata ]

#讀取檔案清單
mypath = os.getcwd()

for key in KeyList:
	print("\nKey  : "+key)
	if not os.path.isdir(mypath+"\\@Sorted"):
		os.mkdir(mypath+"\\@Sorted")
	#讀取先前的清單
	try:
		os.chdir(mypath+"\\@Sorted\\"+key)
		with open("@FileList.txt" , "r") as clog: 
			TitleList2 = [l.strip() for l in clog ]
	except:
		TitleList2 = []
	try:
		os.chdir(mypath+"\\@Sorted\\"+key)
		with open("@CodeList.txt" , "r") as clog: 
			CodeList2 = [l.strip() for l in clog ]
	except:
		CodeList2 = []
	TitleList , CodeList = [],[]

	for root, dirs, files in os.walk(mypath):
		if mypath+"\\@Sorted" in root:
			continue
		if not os.path.isdir(mypath+"\\@Sorted\\"+key):
			os.mkdir(mypath+"\\@Sorted\\"+key)


		os.chdir(root) #更改到當前目錄
		print("\nRoot : "+root+"\n")
	
		for i in files:
			dirpath = mypath
			code = GetCode(i) #從檔名找番號
			if code != None :
				if code not in CodeList:
					x = CoverDL(code,True)
					if x :
						CodeList += [code]
					else :
						continue
				else:
					CoverDL(code,False)

				print("File : "+i)
				fsize = file_size(root+"\\"+i).split(" ") #檢查檔案大小，改檔名
				if fsize[1] == "GB" and float(fsize[0]) >= 4:
					i2 = i.replace(".",".HD.")
					print("Rename : "+i2)
				else:
					i2=i

				if not os.path.isfile(dirpath+"\\"+i2): #若檔案不存在
					os.rename(root+"\\"+i,dirpath+"\\"+i2)
					print("Move : "+dirpath)
				else: #若檔案存在
					file1 = root+"\\"+i
					file2 = dirpath+"\\"+i2
					if hashs(file1) == hashs(file2) : #若存在的檔案相同
						logNprint("*Error : Exist same file \n  *FileName : "+i+"\n  *FilePath : "+root)
					else: #若存在的檔案不同
						for j in range(1,6):
							dotpos = i2.rfind(".")
							i3 = i2[:dotpos]+"-"+str(j)+i2[dotpos:]
							if not os.path.isfile(dirpath+"\\"+i3):
								os.rename(root+"\\"+i,dirpath+"\\"+i3)
								logNprint("*Exist : "+i+"\n *Rename : "+i3)
								print("  Move : "+dirpath)
								break

	os.chdir(mypath+"\\@Sorted\\"+key) #匯出清單
	TitleList += TitleList2
	CodeList += CodeList2
	if len(TitleList) != 0 and len(CodeList) !=0:
		with open("@FileList.txt","w", encoding = 'utf8') as data:
			for i in sorted(TitleList):
				data.write(i+"\n")
		with open("@CodeList.txt","w", encoding = 'utf8') as data:
			for i in sorted(CodeList):
				data.write(i+"\n")

input("\n整理完成，請按Enter離開")