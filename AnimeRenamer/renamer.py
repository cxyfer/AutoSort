# coding=UTF-8
import os , time

mypath = os.getcwd() #執行目錄

def logNprint(text,path=mypath,pr=True):
	logpath=path+"\\"+"rename.log"
	#if not os.path.isfile(logpath):
		#text="#Renamer Programed By GDST/LMI\n"+ text #整理訊息
	if pr :
		print(text)
	with open(logpath,"a", encoding = 'utf-8-sig') as data:
		data.write(str(text)+"\n")

with open("title.txt" , "r", encoding = 'utf-8-sig') as data: 
	List = [l.strip().split("\t",1) for l in data ]
Dic ={}
for i in List:
	Dic[i[0]] = i[1]
KeyList = [ i[0] for i in List ]

name = mypath[mypath.rfind("]")+1:] #作品名稱
for root, dirs, files in os.walk(mypath):
	if mypath == root or mypath+"\\劇場版" in root : #略過特定資料夾
		continue
	
	currenttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) #執行時間
	runtimetext="\n執行時間 : "+currenttime
	logNprint(runtimetext,pr=False,path=root)

	logNprint("\nPath : "+root.replace(mypath,".")+"\n",path=root)
	block = root.replace(mypath+"\\","").split("-") #字幕組&語言&畫質
	lang = block[1] if block[1] == block[-2] else "CHT" #語言(默認CHT)

	for file in sorted(files) :
		print(file)
		if ".txt" in file or ".py" in file or ".part" in file or ".log" in file: #略過
			continue
		if ".ass" in file or ".srt" in file: #略過字幕
			continue
		filepath1 = root + "\\" +file
		#logNprint("File : "+file #原檔案名稱
		file2 = file
		replaceList = ["1080","720","2160","1280","1920","BS11","2019","2018","S01","S02","S03"] #去除會被誤判的數字
		replaceList += [str(year) for year in range(2000,2020)]
		for rep in replaceList:
			file2=file2.replace(rep,"")

		infopos1 = file2.rfind("[")
		infopos2 = file2.rfind("]")
		file2 = file2.replace(file2[infopos1:infopos2+1],"")
		key = 0
		for i in KeyList:
			if file2.find(i) != -1 :
				key = i
				break
		if not key:
			continue
		key2 = key+" END" if "END" in file2 else key
		dotpos = file.rfind(".") #副檔名

		try:
			filename2 = ( "%s (%s)-%s[%s][%s][%s]%s" % (name,block[0],key2,Dic[key],block[-1],lang,file[dotpos:].lower()))
			filepath2 = root + "\\"+ filename2
		except:
			logNprint("*Error : "+file)
			try:
				logNprint(Dic[key])
			except:
				pass
			logNprint(filepath1)
			continue
		if filepath1 == filepath2: #如果已經改名完成
			print("Exist  : "+filename2)
			continue
		if not os.path.isfile(filepath2):
			os.rename(filepath1,filepath2)
			logNprint("File   : "+file,path=root)
			logNprint("Rename : "+filename2,path=root)
input("\n整理完成，請按Enter離開")