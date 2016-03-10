import json
#import sys
import codecs
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

infile = json.load(open('DAC2015.json','r'))
outfile = codecs.open('2015abstracts.txt','w',encoding='utf-8')
csvfile=codecs.open('paper_abstract_years_2015.csv','w',encoding='utf-8')
csvfile.write('title,Abstract,year\n')

for paper in infile:
  title = (paper['Title']).replace('\n','')
  abstract = (paper['Abstract']).replace('\n','')
  outfile.write(title)
  outfile.write(abstract)
  outfile.write('\n')
  csvfile.write(('\"{}\",\"{}\",{}\n'.format(title,abstract,2015)).encode('utf-8'))




