import MySQLdb

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


sql1 = '''
Create view author_paper_map as
SELECT 
    Authors.AuthorID , AuthorName,PaperID
FROM
    Authors join Works on Authors.AuthorID = Works.AuthorID;
'''
sql='''

SELECT 
    author_paper_map.AuthorID AS author_id,
    Works.AuthorId AS coauthor_id,
    author_paper_map.PaperID AS paper_id,
  author_paper_map.AuthorName AS author_name
FROM
    author_paper_map
        JOIN
    Works ON author_paper_map.PaperID = Works.PaperID
WHERE
    author_paper_map.AuthorID != Works.AuthorId
ORDER BY author_id asc  ,paper_id asc
'''

outfile = open('author_coauthor_paper_map.csv','w')
outfile.write('author_id,coauthor_id,paper_id,author_name\n')
#import os
db = MySQLdb.connect("localhost","root","","dac" )
# prepare a cursor object using cursor() method
cursor = db.cursor()
try:
    cursor.execute(sql1)
except Exception:
    pass
cursor.execute(sql)

results = cursor.fetchall()
for row in results:
    outfile.write('{},{},{},"{}"'.format(row[0],row[1],row[2],row[3]))
    outfile.write('\n')
