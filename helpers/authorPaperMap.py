import MySQLdb

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

outfile = open('authors_papers_map.csv','w')
outfile.write('AuthorID,AuthorName,PaperID\n')
#import os
db = MySQLdb.connect("localhost","root","","dac" )
# prepare a cursor object using cursor() method
cursor = db.cursor()
cursor.execute("SELECT AuthorID,PaperID from Works")

results = cursor.fetchall()
for row in results:
    PaperID = row[1]
    AuthorID = row[0]
    cursor2 = db.cursor()
    cursor2.execute("SELECT AuthorName from Authors where AuthorID={}".format(AuthorID))
    AuthorName = cursor2.fetchone()[0]
    outfile.write('{},"{}",{}'.format(AuthorID,AuthorName,PaperID))
    outfile.write('\n')
