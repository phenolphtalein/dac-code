import json
import sys
import os
import re
import codecs
from collections import Counter

'''
paper_file = sys.argv[1]
citation_file = sys.argv[2]
outfile = sys.argv[3]
'''
'''
template = {
'Title':None,
'Year':None,
'Authors':None,
'Topics':None,
'Broad_Topic':None,
'CitationInfo':{
  'total':0,
  'self':0,
  'yearly':{y:[] for y in [0]+range(2002,2016)},
  'yearly_self':{y:[] for y in [0]+range(2002,2016)},
  'organizations':{},
  'journals':{},
  'institutions':{}
  }
}
'''


def dist(sa, sb):
  la=len(sa)
  lb=len(sb)
  if la*lb == 0:
    return la+lb
  m = [[0 for j in range(lb+1)] for i in range(la+1)]
  m[0] = [i for i in range(lb+1)]
  for i in range(la, -1, -1):
    m[i][0] = i
  for i in range(1,la+1):
    for j in range(1, lb+1):
      rem = m[i-1][j]+1
      ins = m[i][j-1]+1
      sub = m[i-1][j-1]if sa[i-1]==sb[j-1] else m[i-1][j-1]+1
      m[i][j] = min(rem,ins,sub)
  return m[la][lb]

def normalize(name):
  name = name.lower().strip()
  name = re.sub('[^a-z]+',' ',name)
  name = re.sub('\s+',' ',name)
  return name.strip()

def is_same_person(c_auth, p_auth):
  try:
    c_auth.decode('ascii')
    p_auth.decode('ascii')
  except UnicodeDecodeError:
    return False
  cname = normalize(c_auth)
  pname = normalize(p_auth)
  distance = dist(cname,pname)
  #print cname, pname, distance
  if distance > 2:
    return False
  cname_parts = cname.split(' ')
  pname_parts = pname.split(' ')
  cinitial = ''.join([x[0] for x in cname_parts])
  pinitial = ''.join([x[0] for x in pname_parts])
  distance = dist(cinitial,pinitial)
  thresh = float(min(len(cname_parts),len(pname_parts)))/2.0
  #print cinitial, pinitial, distance, thresh
  #print ''
  if len(cinitial)!=len(pinitial) or (distance < thresh):
    return True
  return False

def test_self(c_auths, p_auths):
  #print c_auths
  #print p_auths
  for c_auth in c_auths:
    for p_auth in p_auths:
      if is_same_person(c_auth, p_auth):
        return True
  return False

def main():
  paper_file = sys.argv[1]
  citation_file = sys.argv[2]
  outfile = sys.argv[3]
  with codecs.open(paper_file,'r',encoding='utf-8') as papers, codecs.open(citation_file,'r',encoding='utf-8') as citations, codecs.open(outfile,'w',encoding='utf-8') as outfile:
    papers = json.load(papers)
    citations = json.load(citations)
    papers_dict = {p['Title']:p for p in papers}
    citations_dict = {c['Title']:c for c in citations}
    all_stats = []
    print len(papers_dict)
    print len(citations_dict)
    for title,paper in papers_dict.items():
      #if title !="A Fast and Efficient Compact Packing Algorithm for Free-Form Objects":
        #continue
      try:
        citations = citations_dict[title]['Cited by']
      except KeyError:
        continue
      entry = {
              'Title':None,
              'Year':None,
              'Authors':None,
              'Topics':None,
              'Broad_Topic':None,
              'CitationInfo':{
                'total':0,
                'self':0,
                'yearly':{y:[] for y in [0]+range(2002,2016)},
                'yearly_self':{y:[] for y in [0]+range(2002,2016)},
                'organizations':{},
                'journals':{},
                'institutions':{},
                'authors':{}
                }
              }
      entry['Title'] = title
      entry['Year'] = paper['Year']
      entry['Authors'] = paper['Authors']
      try:
        entry['Topics'] = paper['Topics']
        entry['Broad_Topic'] = paper['Broad_Topic']
      except KeyError:
        pass
      jour_dict = {}
      org_dict = {}
      for citation in citations:
        entry['CitationInfo']['total'] = entry['CitationInfo']['total'] + 1
        c_title = citation['title']
        c_year = 0
        c_info = citation['info']
        if len(c_info.keys())>0:
          try:
            c_year = int(c_info['year'])
            if c_year > 2015 or c_year < 2002:
              c_year = 0
            #print title, c_year
          except KeyError:
            pass
          try:
            c_jour = c_info['journal']
            if c_jour not in entry['CitationInfo']['journals']:
              entry['CitationInfo']['journals'][c_jour] = 1
            else:
              entry['CitationInfo']['journals'][c_jour] = entry['CitationInfo']['journals'][c_jour] + 1
          except KeyError:
            pass
          try:
            c_org = c_info['organization']
            if c_org not in entry['CitationInfo']['organizations']:
              entry['CitationInfo']['organizations'][c_org] = 1
            else:
              entry['CitationInfo']['organizations'][c_org] = entry['CitationInfo']['organizations'][c_org] + 1
          except KeyError:
            pass
          try:
            c_inst = c_info['institution']
          except KeyError:
            try:
              c_inst = c_info['school']
            except KeyError:
              c_inst = None
          if c_inst and c_inst not in entry['CitationInfo']['institutions']:
            entry['CitationInfo']['institutions'][c_inst] = 1
          elif c_inst:
            entry['CitationInfo']['institutions'][c_inst] = entry['CitationInfo']['institutions'][c_inst] + 1 
        entry['CitationInfo']['yearly'][c_year].append(c_title)
        try:
          for author in c_info['author']:
            author = author.strip().decode('UTF-8', errors = 'replace')
            if author not in entry['CitationInfo']['authors']:
              entry['CitationInfo']['authors'][author] = 1
            else:
              entry['CitationInfo']['authors'][author] = entry['CitationInfo']['authors'][author] + 1
        except Exception:
          pass
        #print c_year, c_title
        is_self = False
        try:
          is_self = test_self(c_info['author'],paper['Authors'])
        except Exception:
          pass
        if is_self:
          entry['CitationInfo']['self'] = entry['CitationInfo']['self'] + 1
          entry['CitationInfo']['yearly_self'][c_year].append(c_title)
      keys = entry['CitationInfo']['yearly_self'].keys()
      for k in keys:
        if  len(entry['CitationInfo']['yearly_self'][k]) ==0:
          del  entry['CitationInfo']['yearly_self'][k]
      keys = entry['CitationInfo']['yearly'].keys()
      for k in keys:
        if  len(entry['CitationInfo']['yearly'][k]) ==0:
          del  entry['CitationInfo']['yearly'][k]
      all_stats.append(entry)
      
    json.dump(all_stats,outfile,indent=4,ensure_ascii=False)
    return all_stats

def analyse(stats):
  org_count = Counter()
  jour_count = Counter()
  inst_count = Counter()
  years = [0]+range(2002, 2016)

  stat = {'organizations':org_count, 'journals':jour_count, 'institutions':inst_count, 'yearly':{y:[] for y in years},'yearly_nonself':{y:[] for y in years}}
  outfile = codecs.open('citationAnalysis.json','w',encoding='utf-8')


  for entry in stats:
    info = entry['CitationInfo']
    title = entry['Title']

    # count organizations
    org_dict = info['organizations']
    org_count += Counter(org_dict)

    # count journals
    jour_dict = info['journals']
    jour_count += Counter(jour_dict)

    # count institutions
    inst_dict = info['institutions']
    inst_count += Counter(inst_dict)

    yearstat = info['yearly']
    yearstat_self = info['yearly_self']
    for year in yearstat.keys():
      stat['yearly'][year].append((title, len(yearstat[year])))
      stat['yearly_nonself'][year].append((title, len(yearstat[year]) if year not in yearstat_self else len(yearstat[year])-len(yearstat_self[year]) ))


  org_count = [(x[0],x[1]) for x in dict(org_count).items()]
  jour_count = [(x[0],x[1]) for x in dict(jour_count).items()]
  inst_count = [(x[0],x[1]) for x in dict(inst_count).items()]

  # organizations, journals and institutions ranked by how much they cite DAC
  org_count = sorted(org_count, key=lambda x: x[1], reverse=True)
  jour_count = sorted(jour_count, key=lambda x: x[1], reverse=True)
  inst_count = sorted(inst_count, key=lambda x: x[1], reverse=True)

  # papers sorted by the num of citaitions they get each year
  # 0 menas the years the unknown
  # 50 most cited papers 
  for y in stat['yearly'].keys():
    stat['yearly'][y] = sorted(stat['yearly'][y], key=lambda x: x[1], reverse=True)[:50]
  for y in stat['yearly_nonself'].keys():
    stat['yearly_nonself'][y] = sorted(stat['yearly_nonself'][y], key=lambda x: x[1], reverse=True)[:50]
  stat['organizations']=org_count 
  stat['journals']=jour_count
  stat['institutions']=inst_count


  json.dump(stat, outfile, indent=1, ensure_ascii=False, sort_keys=True)

  


if __name__ == "__main__":
  #print is_same_person(sys.argv[1], sys.argv[2])
  all_stats = main()
  analyse(all_stats)

  






