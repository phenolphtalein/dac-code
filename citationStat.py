import json
import sys
import os

paper_file = sys.argv[1]
citation_file = sys.argv[2]
outfile = sys.argv[3]

template = {
'Title':None,
'Year':None,
'Authors':None,
'Topics':None,
'Broad_Topic':None,
'CitationInfo':{
  'total':0,
  'self':0,
  'yearly':{y:[] for y in [0,range(2002,2016)]},
  'yearly_self':{y:[] for y in [0,range(2002,2016)]},
  'organizations':{},
  'journals':{},
  'institutions':{}
  }
}

def is_self(c_auth, p_auth):
  return False 

with open(paper_file,'r') as papers, open(citation_file,'r') as citations, open(outfile,'w') as outfile:
  papers = json.load(papers)
  citaions = json.load(citations)
  papers_dict = {p['Title']:p for p in papers}
  citations_dict = {c['Title']:c for c in citations}
  all_stats = []
  for title,paper in papers_dict.items():
    try:
      citations = citations_dict[title]
    except KeyError:
      continue
    entry = template.copy()
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
          c_year = c_info['year']
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
            continue
        if c_inst not in entry['CitationInfo']['institutions']:
          entry['CitationInfo']['institutions'][c_inst] = 1
        else:
          entry['CitationInfo']['institutions'][c_inst] = entry['CitationInfo']['institutions'][c_inst] + 1

      entry['CitationInfo']['yearly'][c_year].append(c_title)
      is_self = False
      try:
        is_self = is_self(citaion['author'],paper['Authors'])
      except Exception:
        pass
      if is_self:
        entry['CitationInfo']['self'] = entry['CitationInfo']['self'] + 1
        entry['CitationInfo']['yearly_self'][c_year].append(c_title)





