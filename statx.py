import json
import re

'''
count of citations by year
'''

data = json.load(open('output.json','r'))
database = json.load(open('DAC_Entire_Database.json','r'))

stat = {}

for paper in database:
  year = paper['Year']
  if year not in stat:
      stat[year] = {'count':0}
  stat[year]['count'] = stat[year]['count'] + 1 #paper count



for paper in data:
  detc = paper['DETC']
  pattern = re.compile('DETC(\d+)')
  m = pattern.findall(detc)
  if len(m)>0:
    year = int(m[0])
    for citation in paper['Citations']:
      citeyear = citation['Year']
      if citeyear!='':
        if citeyear not in stat[year]:
          stat[year][citeyear] = 0
        stat[year][citeyear] = stat[year][citeyear]+1

stats = {}
years = []
for year, s in stat.items():
  count = {}
  sk = [k for k in s.keys() if k!='count']
  for k in sk:
    if k not in years:
      years.append(k)
    count[k] = float(s[k])/s['count']
  stats[year] = count
years.append(2016)
with open('data.csv','w') as outfile:
  outfile.write('key,value,date\n')
  for year, stat in stats.items():
    for syear in years:
      if syear in stat:
        value = stat[syear]
      else:
        value=0
      outfile.write('{},{},{}\n'.format(str(year),value,str(syear)))



