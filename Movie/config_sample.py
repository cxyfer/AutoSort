#API
TMDbAPI = ""
Rapid_IMDb = ""
dbapi = "https://api.douban.com/v2/movie/search?apikey=0dad551ec0f84ed02907ff5c42e8ec70&q="

#Cookies
##格式為：{'cookie':cookie}，留空則不使用PT搜尋
ourbits = ""
SSD = ""
TJUPT = ""
FRDS = ""
MTeam = ""
PuTao = ""
TTG = ""

#Search
year_check = True #是否在使用豆瓣搜索時檢查年份(若名稱無包含年份則會搜尋不到結果)，建議啟用避免搜尋錯誤

#Rename
CHT_TW = True #優先取台灣譯名，且轉為繁體；若為False則為豆瓣上簡體中文標題
ZH_ENG = True #標題採中英混合；若為False則為僅中文標題 (當觸發ENGlen限制時則不保留英文標題)
ENGlen = 65 #英文標題長度限制，若過長則僅保留中文標題。若不想啟用輸入極大值即可
regSt = True #地區縮寫，使用region.txt文件

#Move
UseRemote = True #將路徑替換為遠端路徑 (讀取掛載信息，但在遠端上操作)
remotepath = "remotepath:" #承上，遠端路徑
pathlen = 200 #路徑長度限制(僅計算資料夾)。若不想啟用輸入極大值即可，觸發後將不建立子資料夾
SubFolder = True #是否保留原始資料夾名稱，將其設為子資料夾 (當觸發config.pathlen限制時則不保留
YearSort = True #老舊電影合併存放

#Log
LogPath = "D:\\AutoSort\\Movie" #默認為執行目錄
LogName = "AutoSort"
DataUpdate = False #資料是否更新，True為會將舊資料更新為新資料且移動資料夾，False會依據資料庫內現有資料做資料夾命名