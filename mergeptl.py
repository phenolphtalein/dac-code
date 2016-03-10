# merge phrase timeline
import json
timeline = json.load(open('phrasetimeline.json','r'))
outfile = open('2015timeline.json','w')
phrases = open('topPhrases.txt','r')

counts = {}
for line in phrases:
  line = line.strip()
  phrase_count = line.split('\t')
  phrase = phrase_count[0]
  count = phrase_count[1]
  counts[phrase] = int(count)

for p in timeline:
  name = p['name']
  if name in counts:
    p['articles'].append([2015,counts[name]])
    p['total'] = p['total'] + counts[name]
    del counts[name]
  else:
    p['articles'].append([2015,0])

for name in counts.keys():
  entry = {}
  entry['name'] = name
  entry['total'] = counts[name]
  if entry['total']<10:
    continue
  entry['articles'] = [[year, 0] for year in range(2002,2015)]
  entry['articles'].append([2015,counts[name]])
  timeline.append(entry)

json.dump(timeline,outfile,indent=4)

