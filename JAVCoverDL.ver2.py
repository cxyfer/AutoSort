# coding: utf-8
import os , requests , urllib , time 
from bs4 import BeautifulSoup

key = input("請輸入番號名稱 : ")
#key = "ABP"

CodeList , TitleList= [] ,[]

def GetCode(filename):
	c = key.upper()+"-"
	if c in filename.upper():
		cpos = filename.upper().find(c)
	elif key.upper() in filename.upper():
		c = key.upper()
		cpos = filename.upper().find(key.upper())
	else:
		return None

	for i in range(len(filename[cpos+len(c):])):
		if not filename[cpos+len(c)+i].isdigit():
			code = filename[cpos:cpos+len(c)+i]
			break

	return code

def CoverDL(code):
	global TitleList
	url = "https://www.javbus.com/"+code
	response = requests.get(url)
	response.encoding = 'UTF-8' 
	soup = BeautifulSoup(response.text, 'lxml')

	if soup.find("h4") == None:
		print("\n*Error : " + code+ " Unknown Error")
		with open("error.log","a", encoding = 'utf8') as erdata:
			erdata.write("\n"+code+"\n")
			erdata.write(str(soup))
		return
	elif soup.find("h4").getText() == "404 Page Not Found!" :
		text = "*Error : " + code+ " 404 Not Found"
		print(text)
		with open("error.log","a", encoding = 'utf8') as erdata:
			erdata.write(text)
		return
		
	article = soup.find("div", {"class": "container"})
	if article == None:
		print("\n*Error : " + code+ " Unknown Error")
		with open("error.log","a", encoding = 'utf8') as erdata:
			erdata.write("\n"+code+"\n")
			erdata.write(str(soup))
		return
	title = article.find("h3").getText()
	imglink = article.find("a", {"class": "bigImage"}).get("href")
	TitleList += [title]

	r = requests.get(imglink)
	filename = title + ".jpg"
	try:
		with open(filename, "wb") as imgdata:
			imgdata.write(r.content)
			print("CoverDL : "+title)
	except:
		with open(code+".jpg", "wb") as imgdata:
			imgdata.write(r.content)
			print("CoverDL : "+title)

#讀取先前的清單
try:
	with open("@FileList.txt" , "r") as clog: 
		TitleList = [l.strip() for l in clog ]
except:
	TitleList = []
try:
	with open("@CodeList.txt" , "r") as clog: 
		CodeList = [l.strip() for l in clog ]
except:
	CodeList = []

#讀取檔案清單
mypath = os.getcwd()
removeList = ['JAVCoverDL.py','JAVList.py',"@FileList.txt","@CodeList.txt""error.log"]
for root, dirs, files in os.walk(mypath):
	for r in removeList:
		if r in files:
			files.remove(r)

	os.chdir(root) #更改到當前目錄
	print("\nPath : "+root)
	
	for i in files:
		code = GetCode(i) #從檔名找番號
		if code not in CodeList and code != None :
			CoverDL(code)
			CodeList += [code]
		else:
			continue

	with open("@FileList.txt","w", encoding = 'utf8') as data:
		for i in sorted(TitleList):
			data.write(i+"\n")
	with open("@CodeList.txt","w", encoding = 'utf8') as data:
		for i in sorted(CodeList):
			data.write(i+"\n")

input("下載完成，請按Enter離開")