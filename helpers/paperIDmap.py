import MySQLdb

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

outfile = open('paperid_titles_map.csv','w')
outfile.write('PaperID,Title,DOI,url\n')
#import os
db = MySQLdb.connect("localhost","root","","dac" )
# prepare a cursor object using cursor() method
cursor = db.cursor()
cursor.execute("SELECT PaperID,Title,DOI,url from Papers")

results = cursor.fetchall()
for row in results:
    PaperID = row[0]
    Title = row[1]
    DOI = row[2]
    url= row[3]
    outfile.write('{},"{}",{},{}'.format(PaperID,Title,DOI,url))
    outfile.write('\n')
