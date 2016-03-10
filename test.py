import nltk
import json
import string
import sys
import codecs
import re
from langdetect import detect

# {<JJ|JJS|JJR>?<NN|NNS|NNP|NNPS>+} 

title = 'introducing business process-oriented knowledge management'
grammar= """
ANP: {<NN|NNS|JJ|JJS|JJR>*<NN|NNS>+}
"""
cp=nltk.RegexpParser(grammar)

def printtree(t, np, anp):
    try:
        t.label()
    except Exception:
        return
    if len(t)>0:
        if t.label() == 'NP':
            npstr= ' '.join([word for word,tag in t.leaves()])
            np.append(npstr)
        if t.label() == 'ANP':
            anpstr= ' '.join([word for word,tag in t.leaves()])
            anp.append(anpstr)
        for c in t:
            printtree(c,np,anp)
p=re.compile('(approach|approache|method|solution|tool)[s]*\s+(for|to)\s+(.*)', re.I)

papers = json.load(open('2015_DAC.json','r'))
'''
papers = [    {
        "PaperID": "DETC2015-46078, pp. V02AT03A004", 
        "Broad_Topic": "Artificial Intelligence and Computational Synthesis", 
        "Title": "Towards Automated Design of Mechanically Functional Molecules", 
        "Abstract": "Metal Organic Responsive Frameworks (MORFs) are a proposed new class of smart materials consisting of a Metal Organic Framework (MOF) with photoisomerizing beams (also known as linkers) that fold in response to light. Within a device these new light responsive materials could provide the capabilities such as photo-actuation, photo-tunable rigidity, and photo-tunable porosity. However, conventional MOF architectures are too rigid to allow isomerization of photoactive sub-molecules. We propose a new computational approach for designing MOF linkers to have the required mechanical properties to allow the photoisomer to fold by borrowing concepts from de novo molecular design and graph synthesis. Here we show how this approach can be used to design compliant linkers with the necessary flexibility to be actuated by photoisomerization and used to design MORFs with desired functionality.", 
        "Year": 2015, 
        "DOI": "doi:10.1115/DETC2015-4607", 
        "Authors": [
            "Charles A. Manion", 
            "Ryan Arlitt", 
            "Irem Tumer", 
            "Matthew I. Campbell", 
            "P. Alex Greaney"
        ], 
        "DETC": "DETC2015-46078", 
        "Topics": [
            "Design"
        ]
    }]
    '''
output = []
for paper in papers:
    title = paper['Title']
    abstract = paper['Abstract']
    title = nltk.word_tokenize(title)
    title = nltk.pos_tag(title) 
    sentences = nltk.sent_tokenize(abstract)
    for sentence in sentences:
        #print(sentence)
        res = p.findall(sentence)
        if len(res)==0:
            continue
        sentence = res[0][2]
        sentence = nltk.word_tokenize(sentence)
        sentence = sentence[:10]
        sentence = nltk.pos_tag(sentence)
        tree = cp.parse(sentence)
        np=[]
        anp=[]
        printtree(tree,np,anp)
        print(anp)
    tree = cp.parse(title)
    np=[]
    anp=[]
    printtree(tree,np,anp)
    print(anp)
    #break
'''
title=title.replace(':',' ').replace(',',' ').replace('?',' ').lower()
title = nltk.word_tokenize(title)
title = nltk.pos_tag(title) 
tree = cp.parse(title)
np=[]
anp=[]
printtree(tree,np,anp)
print(anp)

#with codecs.open('keywords.json','w',encoding='utf-8') as outfile:
#   json.dump(elems,outfile,indent=4,ensure_ascii=False)
'''

