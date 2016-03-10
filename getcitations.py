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
from selenium import webdriver

vpn = 0
opener = None
robot = False
url_base = 'https://scholar.google.com'
driver = None

user_agent = ['Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201','Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A']

req_header = [('user-agent', 'Mozilla/5.0'),('method','GET'),('referer','https://scholar.google.com')]


def edit(sa, sb):
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

def check(ta, tb):
  ta = (ta.lower()).strip()
  tb = (tb.lower()).strip()
  w = (' '.join([ta,tb])).split(' ')
  try:
    ml = max([len(x) for x in w])+2
  except Exception:
    ml = 2
  dist = edit(ta, tb)
  return dist<=ml



def innermost(elem, l, lvl, maxl):
  if lvl>maxl:
    return l
  try:
    elem.contents
  except AttributeError:
    if len(elem.strip()) > 0:
      l.append(elem)
  else:
    for e in elem.contents:
      innermost(e, l, lvl+1, maxl)
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
      if 'No pages were found' not in res:
        robot = True
      return None
    ret = get_link(search_res[0], title)
    if ret is None:
      return None
    cite_num, cite_url = ret
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
  try:
    title_link = (title_elem.find_all('a'))[0]
    rtitle = title_link.text
  except Exception:
    rtitle = innermost(title_elem,[],0,1)
    rtitle = rtitle[0]
  if rtitle is None:
    return None
  rtitle = rtitle.strip()
  if not check(title,rtitle):
    print colored('title mismatch:\n\t{}\n\t{}'.format(title, rtitle), 'magenta')
    return None
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
  global driver
  papers = []
  start = 0
  global robot
  while(1):
    if start >= num:
      break
    if '&start=' not in url:
      url = url_base+url+'&start={}'.format(start)
    else:
      url = re.sub(r'&start=\d+', '&start={}'.format(start),url)
    opener = ul.build_opener()
    opener.addheaders = req_header
    try:
      print colored(url,'blue')
      driver.get(url)
      dom = bs(driver.page_source, 'lxml')
      results = driver.find_elements_by_xpath("//div[@class='gs_r']")
      dom_results = dom.find_all(lambda x: x.name == 'div' and x.get('class') == ['gs_r'])
      if len(results) == 0:
        robot = True
        reconnect()
        continue
      time.sleep(2.5)
      for i,res in enumerate(dom_results):
        p = {'title':'', 'url':'', 'link':'', 'citation':''}
        text_elem = res.find_all(attrs={'class':'gs_ggs gs_fl'})
        if len(text_elem) > 0:
          text_elem = text_elem[0]
          text_link = text_elem.find_all('a')
          if len(text_link) > 0:
            text_link = (text_link[0]).get('href')
            p['link'] = text_link
        title_elem = res.find_all(lambda x: x.name == 'h3' and x.get('class') == ['gs_rt'])[0]
        try:
          title_link = (title_elem.find_all('a'))[0]
          title = title_link.text
          p['url'] = title_link.get('href')
        except Exception:
          title = innermost(title_elem,[],0,1)
          title = title[0]
        title = title.strip()
        if len(title) == 0:
          robot = True
          reconnect()
          continue
        p['title'] = unicode(title)
        btn = driver.find_element_by_xpath("//div[@class='gs_r'][{}]//div[@class='gs_fl'][1]/a[@aria-controls='gs_cit']".format(i+1))
        btn.click()
        e=driver.find_element_by_id('gs_cit0')
        time.sleep(1)
        closebtn = driver.find_element_by_id('gs_cit-x')
        closebtn.click()
        citation = e.text
        if len(citation) == 0:
          robot = True
          reconnect()
          continue
        p['citation'] = citation
        if p['title'] not in [x['title'] for x in papers]:
          papers.append(p)
        time.sleep(2.5)
      start += 10
    except Exception, e:
      robot = True
      reconnect()
      continue

  return papers

def reconnect():
  global driver
  global robot
  robot = False
  if driver:
    driver.quit()
    driver = None
  os.system('/opt/cisco/anyconnect/bin/vpn -s disconnect')
  os.system('echo "2\n{}\n{}\n" | /opt/cisco/anyconnect/bin/vpn -s connect vpn.cites.illinois.edu'.format(sys.argv[3], sys.argv[4]))
  time.sleep(random.randint(5,10))
  if not driver:
    driver = webdriver.Firefox()
    driver.implicitly_wait(25)

      
def main():
  
  global driver
  driver=webdriver.Firefox()
  driver.implicitly_wait(25)
  #papers = json.load(open('DAC_Entire_DataBase.json', 'r'))
  #papers = json.load(open('missing.json', 'r'))
  papers = json.load(open(sys.argv[1], 'r'))
  global robot
  with codecs.open(sys.argv[2],'w',encoding='utf-8') as outfile:
    for paper in papers:
      title = paper['Title']
      DETC = paper['DETC']
      if title is None or len(title)==0:
        continue
      citations = search_citation(title)
      # change ip
      while robot:
        reconnect()
        citations = search_citation(title)
      if citations is not None and len(citations)>0:
        curr = {'Title':title, 'DETC':DETC, 'Cited by':citations}
        json.dump(curr,outfile,indent=4,ensure_ascii=False)
        outfile.write(',\n')
      time.sleep(random.randint(5,10))
    '''
    for title in papers:
      if title is None or len(title)==0:
        continue
      print title
      citations = search_citation(title)
      # change ip
      while robot:
        reconnect()
        citations = search_citation(title)
      if citations is not None and len(citations)>0:
        curr = {'Title':title, 'Cited by':citations}
        json.dump(curr,outfile,indent=4,ensure_ascii=False)
        outfile.write(',\n')
      time.sleep(random.randint(5,10))
    '''
  driver.quit()

def testmain(title):
  citations = search_citation(title)
  if citations is not None and len(citations)>0:
    print len(citations)
  driver.quit()


if __name__ == '__main__':
  if len(sys.argv)<4:
    print 'usage: python citations.py [infile] [outfile] [netid] [password]'
    exit(0)
  main()
  #testmain('Identifying attractive research fields for new scientists')


