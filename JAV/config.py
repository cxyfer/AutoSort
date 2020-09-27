import os

#Main.py
CheckFile = True #是否進行重複檔案杜對

#search.py
tempfolder = "D:\\Cache" #圖片快取存放
MergeAllPreview = True
javdb = "D:\\GoogleDrive\\AutoSort\\javdb.txt"
#signpic = "D:\\GoogleDrive\\AutoSort\\sign.png" #浮水印，留空為不使用
signpic = ""

#sql.py
LogPath = "D:\\GoogleDrive\\AutoSort"
LogName = "JAV.db"

if not os.path.isdir(tempfolder):
	os.mkdir(tempfolder)
if not os.path.isdir(LogPath):
	os.mkdir(LogPath)
