import json
import os
from nltk.stem import WordNetLemmatizer

wnl = WordNetLemmatizer()

dirname = '../dac-network/paper_abstract_years/top_phrases_by_year'
years = range(2002,2016)
filename = 'topPhrases_{}.txt'

out = []
lookup = {}
with open('phraseTimeline2.json','w') as outfile:
  for year in years:
    lines = open(os.path.join(dirname, filename.format(year)), 'r')
    for line in lines:
      line = line.strip().lower()
      phrase_count = line.split('\t')
      phrase = phrase_count[0]
      phrase = ' '.join([wnl.lemmatize(word, 'n') for word in phrase.split()])
      count = int(phrase_count[1])
      if not phrase in lookup:
        entry = {"articles":[[y, 0] for y in years], "total":0, "name":phrase}
        lookup[phrase] = entry
      entry = lookup[phrase]
      entry['articles'][year-2002] = [year, count]
      entry['total'] = entry['total'] + count
  for name in sorted(lookup.keys()):
    entry = lookup[name]
    if entry['total']>4:
      out.append(entry)
  json.dump(out,outfile)

