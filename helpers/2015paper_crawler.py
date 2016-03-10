import urllib2 as ul
import codecs
import sys
import json
import re
from bs4 import BeautifulSoup as bs



url_base = 'http://proceedings.asmedigitalcollection.asme.org/volume.aspx?volumeid='
user_agent = ['Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201','Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A']

req_header = [('user-agent', 'Mozilla/5.0'),('method','GET'),('referer','https://scholar.google.com')]




def innermost(elem):
  try:
    elem.contents
  except AttributeError:
    if len(elem.strip()) > 0:
      return elem
    else:
      return None
  else:
    for e in elem.contents:
      ret = innermost(e)
      if not ret is None:
        return ret



      
def main(volumeid, outfile):
  url = '{}{}'.format(url_base,volumeid)
  opener = ul.build_opener()
  opener.addheaders = req_header
  req = ul.Request(url)
  res_source = opener.open(req).read()
  dom = bs(res_source, 'lxml')
  papers = []
  dom_results = dom.find_all(lambda x: x.name == 'div' and x.get('class') == ['contentTocArticle'])
  dom_results = dom_results[1:]
  for res in dom_results:
    paper = {}
    div_title = res.find_all(attrs={'class':'articleTitle'})[0]
    a_title = div_title.find_all('a')[0]
    URL = a_title.get('href')
    paper['URL'] = 'http://proceedings.asmedigitalcollection.asme.org/{}'.format(URL)
    title = innermost(div_title)
    paper['Title'] = title
    authors = []
    div_auth = res.find_all(attrs={'class':'articleAuthors'})[0]
    a_auths = div_auth.find_all('a')
    for a_auth in a_auths:
      author = innermost(a_auth)
      authors.append(author)
    paper['Authors'] = authors
    div_abst = res.find_all(attrs={'class':'articleAbstract'})[0]
    abst = innermost(div_abst)
    paper['Abstract'] = abst
    div_topics = res.find_all(attrs={'class':'articleTopics'})[0]
    topics = []
    a_topics = div_topics.find_all('a')
    for a_topic in a_topics:
      topic = innermost(a_topic)
      topics.append(topic)
    paper['Topics'] = topics
    span_broadtopic = res.find_all_previous(attrs={'class':'contentTocSubHeading'})[0]
    broad_topic = innermost(span_broadtopic)
    paper['Broad_Topic'] = broad_topic
    div_citation = res.find_all(attrs={'class':'articleCitation'})[0]
    citation = innermost(div_citation)
    pat_doi = re.compile('(doi.*)')
    doi = pat_doi.findall(citation)[0][:-2]
    doi = doi[:-1]
    paper['DOI'] = doi
    pat_DETC = re.compile('(DETC.*)')
    DETC = pat_DETC.findall(citation)[0][:-2]
    paper['DETC'] = DETC
    paper['Year'] = int(citation[:4])
    pat_id = re.compile('(V[A-Z0-9]+)')
    pid = pat_id.findall(citation)[0]
    pid = '{}, pp. {}'.format(DETC,pid)
    paper['PaperID'] = pid
    papers.append(paper)

  json.dump(papers,outfile,indent=4,ensure_ascii=False)
     



if __name__ == '__main__':
  with codecs.open(sys.argv[1],'w',encoding='utf-8') as outfile:
    for vid in [17475,17476]:
      main(vid, outfile)
 


