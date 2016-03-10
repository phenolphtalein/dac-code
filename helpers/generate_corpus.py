import os
import csv

dirname = '../dac-network/paper_abstract_years/'
years = range(2002,2016)
filename = 'paper_abstract_years_{}.csv'
tc=0
ac=0

with open('corpus.txt','w') as outfile, open('titlelist.txt','w') as listfile:
  for year in years:
    infile = open(os.path.join(dirname, filename.format(year)), 'rb')
    reader = csv.DictReader(infile, delimiter=',')
    for row in reader:
        tc+=1
        outfile.write(row['Abstract'])
        outfile.write('\n')
        if len(row['Abstract'])==0:
            print row['title']
            print tc
        ac+=1
        listfile.write(row['title'])
        listfile.write('\n')
        
print ac,tc
