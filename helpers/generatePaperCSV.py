import MySQLdb

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
#select PaperID, DOI, Year, url, Title from Papers 

outfile = open('papers.csv','w')
outfile.write('PaperID, DOI, Year, url, Title\n')
#import os
db = MySQLdb.connect("localhost","root","","dac" )
# prepare a cursor object using cursor() method
cursor = db.cursor()
cursor.execute("SELECT PaperID, DOI, Year, url, Title from Papers")

results = cursor.fetchall()
for row in results:
    PaperID = row[0]
    DOI = row[1]
    Year = row[2]
    url= row[3]
    Title= row[4]
    outfile.write('{},{},{},{},"{}"'.format(PaperID, DOI, Year, url, Title))
    outfile.write('\n')
