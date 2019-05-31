# MVAutoSort

![執行示例](https://i.imgur.com/whiajFm.png)

## 需求套件
pip install requests bs4 lxml fake-useragent opencc-python-reimplemented html2bbcode

## 說明
### 搜尋模式

- 若資料夾名稱含有IMDbID(tt:d)或DoubanID(db_:d)，則使用ID搜尋對應資料

- 若資料夾內存在.nfo檔，則在其中尋找IMDbID，並以此做搜尋

- 若以上皆非，則解析文件夾名稱調用豆瓣API做搜尋

通常文件夾名稱由3個部分組成 $電影名稱.$年份.$壓制參數，目前採用以$年份為錨點解析出$電影名稱的方式 

## 待加入功能

手動模式、搜尋模式 ... (可見參數區)
