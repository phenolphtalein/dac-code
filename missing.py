import json
import codecs

with codecs.open('gscitation.json','r') as infile:
  papers = json.load(infile)
  output = []
  with codecs.open('missing.json','w',encoding='utf-8') as outfile:
    for paper in papers:
      title = paper['Title']
      citations = paper['Cited by']
      missing = []
      for citation in citations:
        if citation['citation'] == '':
          missing.append(citation['title'])
      if len(missing) >0:
        output.append(title)
    json.dump(output,outfile,indent=4,ensure_ascii=False)