#-*- coding: utf-8 -*-
import os, re, requests, math, shutil
from time import sleep as tsleep
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from PIL import Image
import config,sql

ua = UserAgent()
mypath = os.getcwd()

def ImageDL(imgurl): #圖片下載
	r = requests.get(imgurl,headers = {'User-Agent':ua.random})
	filename = imgurl[imgurl.rfind("/")+1:]
	if not os.path.isfile(filename):
		with open(filename, "wb") as imgdata:
			imgdata.write(r.content)
def Merge(code,allpreview,tempfolder="Cache",Column=5,signpic=False): #下載並合併預覽圖
	execdir = tempfolder+"\\"+code
	if not os.path.isdir(execdir):
		os.mkdir(execdir)
	os.chdir(execdir)
	for preview in allpreview:
		ImageDL(preview)
	imgs = [Image.open(fn) for fn in sorted(os.listdir()) if re.match(r'.+?\.jpg|jpeg|png', fn) and not fn.endswith("_preview.jpg")] #打開所有預覽圖

	width,height=0,0
	for img in imgs: #獲取長寬(避免尺寸不一)
		width2 , height2 = img.size 
		width = width2 if width2 > width else width
		height = height2 if height2 > height else height

	result = Image.new(imgs[0].mode,(width*Column,height*(math.ceil(len(imgs)/Column)) ))
	for order,img in enumerate(imgs): #貼上圖片
		width2 , height2 = img.size #尺寸不符的做置中
		result.paste(img, box=(width*(order%Column)+(width-width2)//2 ,height*(order//Column)+(height-height2)//Column ))
	if signpic : #浮水印
		signimg = Image.open(signpic)
		signimg = signimg.convert('RGBA')
		width3 , height3 = signimg.size
		result.paste(signimg, box=(width*Column-width3,height*(math.ceil(len(imgs)/Column))-height3 ) ,mask=signimg )
	result.save(code+"_preview.jpg") #儲存
	return True

def Sort2Dir(key,code,mypath):
	global dirpath 
	number = int(code[code.find("-")+1:])
	order = "%d~%d" % (number-100,number) if number%100 == 0 else "%d~%d" % ((number//100)*100,(number//100+1)*100)
	dirpath = mypath+"\\@~Sorted\\"+key+"\\"+order+"\\"+code
	if not os.path.isdir(dirpath):
		os.makedirs(dirpath)
	os.chdir(dirpath)
	coverfile = code+"_cover.jpg"
	r = requests.get(coverurl,headers = {'User-Agent':ua.random})
	if not os.path.isfile(coverfile) or os.stat(coverfile).st_size == 0:
		with open(coverfile, "wb") as imgdata:
			imgdata.write(r.content)
		print("CoverDL : "+title)

def Database1(key,code,mypath): #搜尋JAVBUS
	global dirpath,title,coverurl
	url = "https://www.javbus.com/"+code
	response = requests.get(url,headers = {'User-Agent':ua.random})
	response.encoding = 'UTF-8' 
	soup = BeautifulSoup(response.text, 'lxml')

	if soup.find("title").getText() == "404 Not Found" or soup.find("title").getText() == "404 Page Not Found! - JavBus":
		return {'success':False,'error':code+" 404 Not Found"}
	elif soup.find("h3") == None:
		return {'success':False,'error':code+" Unknown Error"}
		
	article = soup.find("div", {"class": "container"})
	if article == None:
		return {'success':False,'error':code+" Unknown Error"}

	title = article.find("h3").getText()
	coverurl = article.find("a", {"class": "bigImage"}).get("href")
	allinfo = article.find("div",{"class":"col-md-3 info"}).find_all("p")
	waterfall = article.find("div",{"id":"sample-waterfall"}).find_all("a",{"class":"sample-box"})
	allpreview = [prev.get("href").strip() for prev in waterfall]

	code,date,time,dierector,producer,pulisher,series,genre,actress="","","","","","","","",""
	for nfo in range(len(allinfo)):
		if allinfo[nfo].getText().split(" ")[0] == "識別碼:":
			code = allinfo[nfo].getText().split(" ")[1].strip()
		elif allinfo[nfo].getText().split(" ")[0] == "發行日期:":
			date = allinfo[nfo].getText().split(" ")[1].strip()
		elif allinfo[nfo].getText().split(" ")[0] == "長度:":
			time = allinfo[nfo].getText().split(" ")[1].strip()
		elif allinfo[nfo].getText().split(" ")[0] == "導演:":
			dierector = allinfo[nfo].getText().split(" ")[1].strip()
		elif allinfo[nfo].getText().split(" ")[0] == "製作商:":
			producer = allinfo[nfo].getText().split(" ")[1].strip()
		elif allinfo[nfo].getText().split(" ")[0] == "發行商:":
			pulisher = allinfo[nfo].getText().split(" ")[1].strip()
		elif allinfo[nfo].getText().split(" ")[0] == "系列:":
			series = allinfo[nfo].getText().split(" ")[1].strip()
		elif allinfo[nfo].getText() == "類別:":
			genre = [g.getText().strip() for g in allinfo[nfo+1].find_all("span",{"class":"genre"}) ]
		elif allinfo[nfo].getText() == "演員:":
			actress = [g.getText().strip() for g in allinfo[nfo+1].find_all("span",{"class":"genre"}) ]

	Sort2Dir(key,code,mypath)
	mergename = code+"_preview.jpg"
	mergepath = config.tempfolder+"\\"+code
	if not os.path.isfile(dirpath+"\\"+mergename) and len(allpreview)>0:
		Merge(code,allpreview,tempfolder=config.tempfolder,signpic=config.signpic)
		shutil.move(mergepath+"\\"+mergename,dirpath+"\\"+mergename) #Move
		#shutil.rmtree(mergepath) #清除Cache
	save = [code,title.replace(code,'').strip(),series,",".join(actress),",".join(genre),date,time,dierector,producer,pulisher]
	return {'success':True,'dirpath':dirpath,'code':code,'save':save,'title':title.replace(code,'').strip()}

def Database2(key,code,mypath): #搜尋JAV321
	global dirpath,title,coverurl
	surl = "https://www.jav321.com/search"
	payload = {'sn': code}
	response = requests.post(url=surl, data=payload, headers={'User-Agent':ua.random}) 
	response.encoding = 'UTF-8' 
	soup = BeautifulSoup(response.text, 'lxml')
	if soup.find("div", {"class": "alert"}):
		return {'success':False,'error':soup.find("div", {"class": "alert"}).getText()}

	t1 = soup.find("h3").getText()
	t2 = soup.find("h3").find("small").getText()
	title = code + " " +t1.replace(t2,"").strip()
	imgs = soup.find_all("div","col-xs-12 col-md-12")[:-1]
	imglist = [i.find("img").get("src") for i in imgs]
	coverurl = imglist[0]
	allpreview = imglist[1:]

	allinfo = soup.find("div",{"class":"col-md-9"})
	allinfo = str(allinfo).split("<br/>")

	actress,producer,genre,code,date,time,series="","","","","","",""
	for nfo in allinfo:
		nfo2 = BeautifulSoup(nfo, 'lxml').getText()
		if "女优:" in nfo2:
			actress = nfo2.replace("女优:","").strip().split("   ")
		elif "片商:" in nfo2:
			producer = nfo2.replace("片商:","").strip()
		elif "标签:" in nfo2:
			genre = nfo2.replace("标签:","").strip().split(" ")
		elif "番号:" in nfo2:
			code = nfo2.replace("番号:","").strip().upper()
		elif "发行日期:" in nfo2:
			date = nfo2.replace("发行日期:","").strip()
		elif "播放时长:" in nfo2:
			time = nfo2.replace("播放时长:","").strip().replace("分钟","分鐘")
		elif "系列:" in nfo2:
			series = nfo2.replace("系列:","").strip()
 
	Sort2Dir(key,code,mypath)
	mergename = code+"_preview.jpg"
	mergepath = config.tempfolder+"\\"+code
	if not os.path.isfile(dirpath+"\\"+mergename) and len(allpreview)>0:
		Merge(code,allpreview,tempfolder=config.tempfolder,signpic=config.signpic)
		shutil.move(mergepath+"\\"+mergename,dirpath+"\\"+mergename) #Move
		#shutil.rmtree(mergepath) #清除Cache
	save = [code,title.replace(code,'').strip(),series,",".join(actress),",".join(genre),date,time,'',producer,'']
	return {'success':True,'dirpath':dirpath,'code':code,'save':save,'title':title.replace(code,'').strip()}

#shutil.rmtree(config.tempfolder) #清除Cache

'''#Test
res = Database1("MDTM","MDTM-550",mypath)
db_name = "%s\\%s" % (config.LogPath,config.LogName) if config.LogPath else config.LogName
sql.input(db_name, 'JAV', save,replace=True)'''