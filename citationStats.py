import sys
import json
import codecs

def copen(filename, opt):
  codecs.open(filename,opt,encoding='utf-8')

data_file_name, citation_file_name, outfile_name = sys.argv[1:]
with copen(data_file_name,'r') as data_file, copen(citation_file_name, 'r') as citation_file, copen(outfile_name,'w') as outfile:
  data_json = json.load(data_file)
  citation_json = json.load(citation_file)
  data_dict = {x['Title']:x for x in data_json}
  citation_dict = {c['Title']:c for c in citation_json}
  outdict = {}
  for title, paper in data_dict.items():
    try:
      citations = citation_dict[title]
    except KeyError:
      continue
    if paper['DETC'] != citations['DETC']:
      continue
    total_citation = len(citations['Cited by'])

