#-*- coding: utf-8 -*-
import os, re, requests, math, shutil
from bs4 import BeautifulSoup
from time import sleep
from user_agent import generate_user_agent
import http.cookiejar
from PIL import Image
import config, sql

#UA = UserAgent().random
UA = generate_user_agent()
mypath = os.getcwd()

def ImageDL(imgurl,filename): #圖片下載
	r = requests.get(imgurl,headers = {'User-Agent':UA},stream=True)
	with open(filename, "wb") as imgdata:
		imgdata.write(r.content)
	if 'Content-Length' in r.headers.keys() and os.stat(filename).st_size != int(r.headers['Content-Length']): #檢查檔案大小，避免下載失敗
		ImageDL(imgurl)
def Merge(code,allpreview,tempfolder="Cache",signpic=False): #下載並合併預覽圖
	execdir = tempfolder+"\\"+code

	if not os.path.isdir(execdir):
		os.mkdir(execdir)
	os.chdir(execdir)
	for preview,prenum in zip(allpreview,range(len(allpreview))):
		preview = preview[:preview.rfind("?")]
		filename = "pre%02d_%s" % (prenum,preview[preview.rfind("/")+1:])
		if not os.path.isfile(filename):
			ImageDL(preview,filename)
	try:
		imgs = [Image.open(fn) for fn in sorted(os.listdir()) 
		if re.match(r'.+?\.(jpg|jpeg|png)', fn) and not fn.endswith("_preview.jpg") and os.stat(fn).st_size > 0] #打開所有預覽圖
	except OSError:
		try:
			shutil.rmtree(execdir)
		except PermissionError:
			return False
		Merge(code,allpreview,tempfolder,signpic)
		return True
	width,height=0,0
	for img in imgs: #獲取長寬(避免尺寸不一)
		width2 , height2 = img.size 
		width = width2 if width2 > width else width
		height = height2 if height2 > height else height

	if len(imgs) <= 5: Column =len(imgs)
	elif len(imgs)%5 == 0: Column =5
	elif len(imgs)%4 == 0: Column =4
	elif len(imgs)%3 == 0: Column =3
	else: Column =5
	result = Image.new(imgs[0].mode,(width*Column,height*(math.ceil(len(imgs)/Column)) ))
	for order,img in enumerate(imgs): #貼上圖片
		width2 , height2 = img.size #尺寸不符的做置中
		result.paste(img, box=(width*(order%Column)+(width-width2)//2 ,height*(order//Column)+(height-height2)//2 ))
	if signpic : #浮水印
		signimg = Image.open(signpic)
		signimg = signimg.convert('RGBA')
		width3 , height3 = signimg.size
		result.paste(signimg, box=(width*Column-width3,height*(math.ceil(len(imgs)/Column))-height3 ) ,mask=signimg )
	result.save(code+"_preview.jpg") #儲存
	return True

def Sort2Dir(key,code,mypath,mode=1,sub=''):
	global dirpath
	if key == "T28": #特殊番號例外處理
		code = code.replace("T-28","T28-")
	number = int(code[code.find("-")+1:])
	if mode ==1:
		order = "%03d~%03d" % (number-100+1,number) if number%100 == 0 else "%03d~%03d" % ((number//100)*100+1,(number//100+1)*100)
		dirpath = mypath+"\\@~Sorted\\"+key+"\\"+order+"\\"+code
	elif mode ==2: #FC2
		sub = sub.replace(":","：")
		dirpath = mypath+"\\@~Sorted\\@"+key+"\\"+sub+"\\"+code
	if not os.path.isdir(dirpath):
		os.makedirs(dirpath)
	os.chdir(dirpath)
	if coverurl==None or not coverurl:
		print("*Error : No Cover.")
		return

	coverfile = code+"_cover.jpg"
	r = requests.get(coverurl,headers = {'User-Agent':UA})
	if not os.path.isfile(coverfile) or os.stat(coverfile).st_size == 0:
		with open(coverfile, "wb") as imgdata:
			imgdata.write(r.content)
	os.chdir(dirpath[:dirpath.rfind("\\")])
	coverfile2 = title+".jpg"
	if not os.path.isfile(coverfile) and not os.path.isfile(coverfile2):
		try:
			with open(coverfile2, "wb") as imgdata:
				imgdata.write(r.content)
		except:
			with open(code+".jpg", "wb") as imgdata:
				imgdata.write(r.content)
		print("CoverDL : "+title)

def Database1(key,code,mypath): #搜尋JAVBUS
	global dirpath,title,coverurl
	url = "https://www.javbus.com/"+code
	response = requests.get(url,headers = {'User-Agent':UA})
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
	code,date,time,dierector,producer,pulisher,series,genre,actress,allpreview="","","","","","","","","",[]
	if article.find("div",{"id":"sample-waterfall"}):
		waterfall = article.find("div",{"id":"sample-waterfall"}).find_all("a",{"class":"sample-box"})
		allpreview = [prev.get("href").strip() for prev in waterfall]
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
			if nfo+1 < len(allinfo):
				actress = [g.getText().strip() for g in allinfo[nfo+1].find_all("span",{"class":"genre"}) ]
	Sort2Dir(key,code,mypath)
	os.chdir(mypath)
	mergename = code+"_preview.jpg"
	mergepath = config.tempfolder+"\\"+code
	if not os.path.isfile(dirpath+"\\"+mergename) and len(allpreview)>0:
		mergeres = Merge(code,allpreview,tempfolder=config.tempfolder,signpic=config.signpic)
		if mergeres:
			shutil.move(mergepath+"\\"+mergename,dirpath+"\\"+mergename) #Move
		#shutil.rmtree(mergepath) #清除Cache
	save = [code,title.replace(code,'').strip(),series,",".join(actress),",".join(genre),date,time,dierector,producer,pulisher]
	return {'success':True,'dirpath':dirpath,'code':code,'save':save,'title':title.replace(code,'').strip()}

def Database2(key,code,mypath): #搜尋JAV321
	global dirpath,title,coverurl
	surl = "https://www.jav321.com/search"
	payload = {'sn': code}
	response = requests.post(url=surl, data=payload, headers={'User-Agent':UA}) 
	response.encoding = 'UTF-8' 
	soup = BeautifulSoup(response.text, 'lxml')
	if soup.find("div", {"class": "alert"}):
		return {'success':False,'error':soup.find("div", {"class": "alert"}).getText()}
	elif soup.find("h3") == None:
		return {'success':False,'error':'Unknown Error'}

	t1 = soup.find("h3").getText()
	t2 = soup.find("h3").find("small").getText()
	title = code + " " +t1.replace(t2,"").strip()
	imgs = soup.find_all("div","col-xs-12 col-md-12")[:-1]
	imglist = [i.find("img").get("src") for i in imgs]
	if len(imglist) == 0:
		return {'success':False,'error':"No Cover."}
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
			code = key+code[code.find("-"):]
		elif "发行日期:" in nfo2:
			date = nfo2.replace("发行日期:","").strip()
		elif "播放时长:" in nfo2:
			time = nfo2.replace("播放时长:","").strip().replace("分钟","分鐘")
		elif "系列:" in nfo2:
			series = nfo2.replace("系列:","").strip()
 
	Sort2Dir(key,code,mypath)
	os.chdir(mypath)
	mergename = code+"_preview.jpg"
	mergepath = config.tempfolder+"\\"+code
	if not os.path.isfile(dirpath+"\\"+mergename) and len(allpreview)>0:
		mergeres = Merge(code,allpreview,tempfolder=config.tempfolder,signpic=config.signpic)
		if mergeres:
			shutil.move(mergepath+"\\"+mergename,dirpath+"\\"+mergename) #Move
		#shutil.rmtree(mergepath) #清除Cache
	save = [code,title.replace(code,'').strip(),series,",".join(actress),",".join(genre),date,time,'',producer,'']
	return {'success':True,'dirpath':dirpath,'code':code,'save':save,'title':title.replace(code,'').strip()}

def Database3(key,code,mypath,cookies=config.javdb): #搜尋JAVDB
	global dirpath,title,coverurl

	re_code = re.search(r"(\d+)([a-zA-Z]+-?.+)",code)
	url = "https://javdb.com/videos/search_autocomplete.json?q="+ (re_code.group(2) if re_code else code)
	vurl = ""

	cookies = http.cookiejar.MozillaCookieJar(cookies)
	cookies.load()

	res = requests.get(url,headers = {'User-Agent':UA},cookies=cookies)
	res.encoding = 'UTF-8' 
	res = res.json() # return dict

	if len(res)==0:
		return {'success':False,'error':code+" not found, return empty json."}
	for r in res:
		if r['number'] == (re_code.group(2) if re_code else code):
			vurl = "https://javdb.com/v/" + r['uid']
	if not vurl:
		return {'success':False,'error':code+" not found, can't find this video."}

	res = requests.get(vurl,headers = {'User-Agent':UA},cookies=cookies)
	res.encoding = 'UTF-8' 
	soup = BeautifulSoup(res.text, 'lxml')

	title = soup.find("h2").getText().strip()
	try:
		if soup.find("img",{"class":"video-cover"}):
			coverurl = soup.find("img",{"class":"video-cover"}).get("src")

		elif soup.find("video",{"id":"preview-video"}):
			coverurl = soup.find("video",{"id":"preview-video"}).get("poster")
		else:
			coverurl = soup.find("div",{"class":"column is-three-fifths column-video-cover"}).find("a").get("href")
	except AttributeError:
		sleep(1)
		return {'success':False,'error':code+' AttributeError'}
	allinfo = soup.find_all("div",{"class":"panel-block"})[:-1] #去除最後一行

	date,time,dierector,producer,pulisher,seller,series,genre,actress,allpreview="","","","","","","","","",[]
	if soup.find("div",{"class":"tile-images preview-images"}):
		waterfall = soup.find("div",{"class":"tile-images preview-images"}).find_all("a",{"class":"tile-item"})
		allpreview = [prev.get("href").strip() for prev in waterfall]
	for nfo in allinfo:
		if nfo.find("strong").getText() == "番號":
			code = nfo.find("span",{"class":"value"}).getText()
		elif nfo.find("strong").getText() == "時間:":
			date = nfo.find("span",{"class":"value"}).getText()
		elif nfo.find("strong").getText() == "時長:":
			time = nfo.find("span",{"class":"value"}).getText()
		elif nfo.find("strong").getText() == "導演:":
			dierector = nfo.find("span",{"class":"value"}).getText()
		elif nfo.find("strong").getText() == "片商:":
			producer = nfo.find("span",{"class":"value"}).getText()
		elif nfo.find("strong").getText() == "發行:":
			pulisher = nfo.find("span",{"class":"value"}).getText()
		elif nfo.find("strong").getText() == "系列:":
			series = nfo.find("span",{"class":"value"}).getText()
		elif nfo.find("strong").getText() == "賣家:":
			seller = nfo.find("span",{"class":"value"}).getText()
			dierector = seller
		elif nfo.find("strong").getText() == "類別:":
			genre = [g.getText().strip() for g in nfo.find("span",{"class":"value"}).find_all("a") ]
		elif nfo.find("strong").getText() == "演員:":
			actress = [g.getText().strip() for g in nfo.find("span",{"class":"value"}).find_all("a") ]

	if key in ["FC2"]:
		Sort2Dir(key,code,mypath,mode=2,sub=seller)
		sleep(1)
	else:
		Sort2Dir(key,code,mypath)
	os.chdir(mypath)
	mergename = code+"_preview.jpg"
	mergepath = config.tempfolder+"\\"+code
	if not os.path.isfile(dirpath+"\\"+mergename) and len(allpreview)>0:
		mergeres = Merge(code,allpreview,tempfolder=config.tempfolder,signpic=config.signpic)
		if mergeres:
			shutil.move(mergepath+"\\"+mergename,dirpath+"\\"+mergename) #Move
		#shutil.rmtree(mergepath) #清除Cache
	save = [code,title.replace(code,'').strip(),series,",".join(actress),",".join(genre),date,time,dierector,producer,pulisher]
	return {'success':True,'dirpath':dirpath,'code':code,'save':save,'title':title.replace(code,'').strip()}


def Database4(key,code,mypath): #搜尋JAVDB
	global dirpath,title,coverurl

	re_code = re.search(r"(\d+)(.+-?.+)",code)
	url = "https://javdb.com/videos/search_autocomplete.json?q="+re_code.group(2) if re_code else code
	vurl = ""

#shutil.rmtree(config.tempfolder) #清除Cache
'''
#Test
res = Database3("300MIUM","300MIUM-670",mypath)
#res = Database3("ORE","ORE-670",mypath)
print(res)

db_name = "%s\\%s" % (config.LogPath,config.LogName) if config.LogPath else config.LogName
sql.input(db_name, 'JAV', save,replace=True)'''