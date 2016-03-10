import urllib2 as ul
import urllib
import cookielib
import codecs
import sys
import json
import time
import random
from termcolor import colored
import re
import os
from bs4 import BeautifulSoup as bs

opener = None
robot = False
url_base = 'https://scholar.google.com'

user_agent = ['Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201','Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A']

req_header = [('user-agent', 'Mozilla/5.0'),('method','GET'),('referer','https://scholar.google.com')]

def innermost(elem, l):
  try:
    elem.contents
  except AttributeError:
    if len(elem.strip()) > 0:
      l.append(elem)
  else:
    for e in elem.contents:
      innermost(e, l)
  return l

def search_citation(title):
  search_url = 'https://scholar.google.com/scholar?hl=en&q='+urllib.quote(title.encode('utf8'))
  print search_url
  global opener
  global robot
  if opener is None:
    cj = cookielib.LWPCookieJar()
    handler = ul.HTTPCookieProcessor(cj)
    opener = ul.build_opener(handler, ul.HTTPHandler())
  header = {'user-agent': user_agent[random.randint(0,len(user_agent)-1)],'method':'GET','referer':'https://scholar.google.com'}
  try:
    req = ul.Request(search_url, headers = header)
    res = opener.open(req).read()
  except Exception, e:
    print colored(e, 'red')
    if '503' in str(e):
      robot = True
      print colored('*****robot*****', 'red')
    return None

  if 'not a robot' in res:
    robot = True
    print colored('*****robot*****', 'red')
    return None
  robot = False
  try:
    dom = bs(res,'lxml')
    # search result for title
    search_res = dom.find_all(attrs={'class':'gs_r'})
    if len(search_res) == 0:
      print >> sys.stderr, 'Paper not found: {}'.format(title)
      return None
    ret = get_link(search_res[0], title)
    print colored(ret, 'green')
    if ret is None:
      return None
    cite_num, cite_url = ret
    print colored('********'+str(cite_num)+'********', 'green')
    papers = get_papers(cite_num, cite_url)
    if papers is None:
      return None
    if len(papers) == 0:
      return None
    return papers
  except Exception, e:
    print colored(e, 'red')
    return None
  


def get_link(gsr, title):
  # check
  title_elem = gsr.find_all(lambda x: x.name == 'h3' and x.get('class') == ['gs_rt'])[0]
  title_link = title_elem.find_all('a')
  if len(title_link) == 0:
    return None
  title_link = title_link[0]
  rtitle = title_link.text
  if rtitle is None:
    return None
  if (title.strip()).lower()!=(rtitle.strip()).lower():
    print colored('title mismatch', 'blue')
    print colored(title, 'blue')
    print colored(rtitle, 'blue')
  # get links
  links_elem = gsr.find_all(lambda x: x.name == 'div' and x.get('class') == ['gs_fl'])
  if len(links_elem) == 0:
    return None
  cite_link = links_elem[0].find_all('a')[0]
  link_txt = cite_link.contents[0]
  if 'Cited by' not in link_txt:
    return None
  cite_num = int(re.findall('(\d+)', link_txt)[0])
  cite_url = cite_link.get('href')
  return cite_num, cite_url


def get_papers(num, url):
  papers = []
  start = 0
  global robot
  while len(papers) < num:
    if '&start=' not in url:
      url = url_base+url+'&start={}'.format(start)
    else:
      url = re.sub(r'&start=\d+', '&start={}'.format(start),url)
    opener = ul.build_opener()
    opener.addheaders = req_header
    try:
      resstr = (opener.open(url)).read()
      dom = bs(resstr, 'lxml')
      results = dom.find_all(lambda x: x.name == 'div' and x.get('class') == ['gs_r'])
      if len(results) == 0:
        return papers
      for res in results:
        p = {'title':'', 'url':'', 'link':''}
        text_elem = res.find_all(attrs={'class':'gs_ggs gs_fl'})
        if len(text_elem) > 0:
          text_elem = text_elem[0]
          text_link = text_elem.find_all('a')
          if len(text_link) > 0:
            text_link = (text_link[0]).get('href')
            p['link'] = text_link
        title_elem = res.find_all(lambda x: x.name == 'h3' and x.get('class') == ['gs_rt'])[0]
        title_link = (title_elem.find_all('a'))[0]
        title = title_link.text
        p['title'] = unicode(title)
        p['url'] = title_link.get('href')
        papers.append(p)
      start += 10
    except Exception, e:
      print colored(e, 'red')
      if 'not a robot' in resstr:
        robot = True
        return None
      return papers
  return papers

      
def main():
  papers = json.load(open('DAC_Entire_DataBase.json', 'r'))
  global robot
  with codecs.open(sys.argv[1],'w',encoding='utf-8') as outfile:
    for paper in papers:
      title = paper['Title']
      DETC = paper['DETC']
      year = paper['Year']
      if title is None or len(title)==0:
        continue
      citations = search_citation(title)
      while robot:
        os.system('/opt/cisco/anyconnect/bin/vpn -s disconnect')
        os.system('echo "2\n{}\n{}\n" | /opt/cisco/anyconnect/bin/vpn -s connect vpn.cites.illinois.edu'.format(sys.argv[2], sys.argv[3]))
        time.sleep(random.randint(1,5))
        robot = False
        citations = search_citation(title)
      if citations is not None and len(citations)>0:
        curr = {'Title':title, 'DETC':DETC, 'Cited by':citations, 'Year':year}
        json.dump(curr,outfile,indent=4,ensure_ascii=False)
        outfile.write(',\n')






if __name__ == '__main__':
  main()


