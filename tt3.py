import os , requests
from bs4 import BeautifulSoup
class DL:
	def Cover2(code):
		global title , dirpath ,imglink
		url = "https://www.jav321.com/video/"+code
		response = requests.get(url)
		response.encoding = 'UTF-8' 
		soup = BeautifulSoup(response.text, 'lxml')

		t1 = soup.find("h3").getText()
		t2 = soup.find("h3").find("small").getText()
		title = code + " " +t1.replace(t2,"")

		if  t1.replace(t2,"") == " ":
			text = "*Error : " + code+ " 404 Not Found"
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

		for img in imglist:
			dotpos = img.rfind("/")
			filename = img[dotpos+1:]

			r = requests.get(img)
			if not os.path.isfile(filename):
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

mypath = os.getcwd() #執行目錄
key = "300NTK"
if not os.path.isdir(mypath+"\\@~Sorted"):
	os.mkdir(mypath+"\\@~Sorted")
if not os.path.isdir(mypath+"\\@~Sorted\\"+key):
	os.mkdir(mypath+"\\@~Sorted\\"+key)

DL.Cover2("300NTK-070")