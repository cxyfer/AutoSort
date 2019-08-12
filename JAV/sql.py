#!/usr/bin/python
import sqlite3 ,re ,config

def init(db_name,table_name):
	conn = sqlite3.connect(db_name)
	cursor = conn.cursor()
	execute = '''CREATE TABLE IF NOT EXISTS %s
		(Code INT PRIMARY KEY NOT NULL,
		標題 TEXT NOT NULL,
		系列 TEXT,
		女優 TEXT,
		類別 TEXT,
		日期 VARCHAR(10) ,
		時長 VARCHAR(10) ,
		導演 TEXT,
		製作商 TEXT,
		發行商 TEXT,
		UNIQUE(Code)
		)''' % (table_name)
	cursor.execute(execute)
	cursor.close()
	conn.close()

def input(db_name,table_name,List,many=False,replace=False):
	num = len(List[0]) if many else len(List)
	conn = sqlite3.connect(db_name)
	cursor = conn.cursor()
	pattern = "IGNORE" if not replace else "REPLACE"
	execute = 'INSERT OR %s INTO %s VALUES (?%s)' % (pattern,table_name,",?"*(num-1))
	if many : #如果是批量資料(蜂巢迴圈)
		cursor.executemany(execute,List)
	else:
		cursor.execute(execute,List)
	conn.commit()
	cursor.close()
	conn.close()

def output(db_name,table_name,file_name):
	with open(file_name, "w", encoding = 'utf-8-sig') as write_file:
		conn = sqlite3.connect(db_name)
		cursor = conn.cursor()
		execute = "SELECT * FROM %s" % (table_name)
		for row in cursor.execute(execute):
			writeRow = "\t".join('%s' % r for r in row)+"\n"
			write_file.write(writeRow)
def query(db_name,table_name,sid):
	conn = sqlite3.connect(db_name)
	cursor = conn.cursor()
	execute = "SELECT * From %s WHERE SID = ?" % (table_name)
	result = cursor.execute(execute, [sid]).fetchone()
	cursor.close()
	conn.close()

#Init
db_name = "%s\\%s" % (config.LogPath,config.LogName) if config.LogPath else config.LogName
init(db_name,"JAV")