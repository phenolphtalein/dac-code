#!/usr/bin/env python
import MySQLdb
import json
from unidecode import unidecode
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
#import os
db = MySQLdb.connect("localhost","root","","dac" )
# prepare a cursor object using cursor() method
cursor = db.cursor()
# execute SQL query using execute() method.
cursor.execute("SELECT MAX(PaperId) from Papers")
current_pid  = cursor.fetchone()[0]
current_pid = int(current_pid)+1

cursor.execute("SELECT MAX(AuthorID) from Authors")
current_aid  = cursor.fetchone()[0]
current_aid = int(current_aid)+1

cursor.execute("SELECT MAX(workId) from Works")
current_wid  = cursor.fetchone()[0]
current_wid = int(current_wid)+1

print current_aid, current_pid, current_wid 

#cursor.execute("SELECT * from Authors where AuthorId=8000")


papers = json.load(open('DAC2015.json','r'))
for paper in papers:
    title = paper['Title']
    year = 2015
    doi = paper['DOI']
    abstract = paper['Abstract']
    url = paper['URL']
    numauthors = len(paper['Authors'])
    pid = current_pid
    sql = """INSERT INTO Papers(PaperID,Title,DOI,NumAuthors,url,Year,PublicationName,Abstract,IsDAC,IsASME,Pages)
                        VALUES ({},\"{}\",\"{}\",{},\"{}\",NULL,\"{}\",\"{}\",NULL,NULL,NULL)""".format(pid,title,doi,numauthors,url,"DAC Conference 2015",abstract)
    try:
        cursor.execute(sql)
        db.commit()
        current_pid+=1
    except Exception as e:
        print e
        db.rollback()  
    for author in paper['Authors']:
        authorstr = unidecode(author)
        cursor.execute("SELECT AuthorID from Authors where AuthorName=\"{}\"".format(authorstr))
        aid  = cursor.fetchone()
        if aid is None:
            aid = current_aid
            sql = """INSERT INTO Authors(AuthorID,AuthorName,EmailID,CloseNessScore,DegreeScore,url)
                        VALUES ({},\"{}\",NULL,NULL,NULL,NULL)""".format(aid,authorstr)
            try:
                cursor.execute(sql)
                db.commit()
                current_aid+=1
            except Exception as e:
                print e
                db.rollback()           
        else:
            aid = aid[0]
        sql = """INSERT INTO Works(AuthorId,PaperId,workId)
                        VALUES ({},{},{})""".format(aid,pid,current_wid)
        try:
                cursor.execute(sql)
                db.commit()
                current_wid+=1
        except Exception as e:
                print e
                db.rollback()


    #break



