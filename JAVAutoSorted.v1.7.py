# coding: utf-8
import os , requests , urllib , time 
from bs4 import BeautifulSoup

key = input("請輸入番號名稱 : ")
#key = "IPX"

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

	if soup.find("title").getText() == "404 Not Found" or soup.find("title").getText() == "404 Page Not Found! - JavBus":
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

	if os.path.isdir(mypath+"\\@Sorted\\"+title):
		dirpath = mypath+"\\@Sorted\\"+title
	elif os.path.isdir(mypath+"\\@Sorted\\"+code):
		dirpath = mypath+"\\@Sorted\\"+code
	else:	
		try:
			os.mkdir(mypath+"\\@Sorted\\"+title)
			dirpath = mypath+"\\@Sorted\\"+title
		except:
			os.mkdir(mypath+"\\@Sorted\\"+code)
			dirpath = mypath+"\\@Sorted\\"+code
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
#讀取先前的清單
try:
	with open("@FileList.txt" , "r") as clog: 
		TitleList2 = [l.strip() for l in clog ]
except:
	TitleList2 = []
try:
	with open("@CodeList.txt" , "r") as clog: 
		CodeList2 = [l.strip() for l in clog ]
except:
	CodeList2 = []
TitleList , CodeList = [],[]

#讀取檔案清單
mypath = os.getcwd()
removeList = ['JAVCoverDL.py','JAVList.py',"","@CodeList.txt""error.log"]
for root, dirs, files in os.walk(mypath):
	for r in removeList:
		if r in files:
			files.remove(r)
	if mypath+"\\@Sorted" in root:
		continue
	if not os.path.isdir(mypath+"\\@Sorted"):
		os.mkdir(mypath+"\\@Sorted")

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
			try:
				print("File : "+i)
				os.rename(root+"\\"+i,dirpath+"\\"+i)
				print("Move : "+dirpath)
			except:
				fsize = file_size(root+"\\"+i).split(" ")
				if fsize[1] == "GB" and float(fsize[0]) >= 4:
					i2 = i.replace(".",".HD.")
					try:
						os.rename(root+"\\"+i,dirpath+"\\"+i2)
						print("Move : "+dirpath)
						continue
					except:
						pass
				logNprint("*Error : "+i+"\n *FilePath : "+root+"\n *Exist in : "+dirpath)
		else:
			continue

os.chdir(mypath) #匯出清單
TitleList += TitleList2
CodeList += CodeList2
with open("@FileList.txt","w", encoding = 'utf8') as data:
		for i in sorted(TitleList):
			data.write(i+"\n")
with open("@CodeList.txt","w", encoding = 'utf8') as data:
		for i in sorted(CodeList):
			data.write(i+"\n")

input("\n整理完成，請按Enter離開")