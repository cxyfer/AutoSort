# coding: utf-8
##Local Ver
#使用本地資料，不爬取

import os , requests , time ,filecmp ,hashlib

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

#要處理的番號清單
with open("data.txt" , "r", encoding = 'utf_8_sig') as keydata: 
	DataList = [l.strip().split(" ",1) for l in keydata ]
Dic = {}
for i in DataList:
	Dic[i[0]] = i[1]

mypath = os.getcwd() #執行目錄

for root, dirs, files in os.walk(mypath):
	if mypath+"\\@~Sorted" in root or mypath+"\\@" in root : #略過根目錄下帶有@的資料夾 (特製)
		continue
	if not os.path.isdir(mypath+"\\@~Sorted\\"):
		os.mkdir(mypath+"\\@~Sorted\\")
	os.chdir(root) #更改到當前目錄
	print("\nPath : "+root)
	
	for key in Dic.keys():
		for i in files:
			if key.upper() in i.upper() or key.upper().replace("-","",1) in i.upper(): #如果能夠從檔案名稱找出番號
				print("Code :",key)
				dirpath = mypath+"\\@~Sorted\\"+key+" "+Dic[key]
				if not os.path.isdir(dirpath):
					os.mkdir(dirpath)
				print("File : "+i)
				fsize = file_size(root+"\\"+i).split(" ") #檢查檔案大小

				if not os.path.isfile(dirpath+"\\"+i): #若檔案不存在
					os.rename(root+"\\"+i,dirpath+"\\"+i)
					print("Move : "+dirpath)
				else: #若檔案存在
					file1 = root+"\\"+i
					file2 = dirpath+"\\"+i2
					if CheckFile and file_size(file1) == file_size(file2) : #若需要比對檔案，且存在的檔案相同
					#if CheckFile and file_size(file1) == file_size(file2) and hashs(file1) == hashs(file2) : #若需要比對檔案，且存在的檔案相同
						os.remove(file1)
						Log.NPrint("*Error : Exist same file \n  *Remove : "+file1)
					else: #若存在的檔案不同
						for j in range(1,10):
							dotpos = i2.rfind(".")
							i3 = i2[:dotpos]+"~"+str(j)+i2[dotpos:]
							if not os.path.isfile(dirpath+"\\"+i3):
								os.rename(root+"\\"+i,dirpath+"\\"+i3)
								Log.NPrint("*Exist : "+i+"\n *Rename : "+i3)
								print("Move : "+dirpath)
								break
input("\n整理完成，請按Enter離開")