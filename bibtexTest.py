#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2 as ul
import urllib
import cookielib
import codecs
import sys
import json
import time
import random
import socket
from termcolor import colored
import re
import os
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import bibtexparser
from inspect import currentframe
from pyvirtualdisplay import Display

def ptline():
    cf = currentframe()
    print colored('----------LINE {}----------'.format(cf.f_back.f_lineno), 'red')


reload(sys)
sys.setdefaultencoding('utf-8')

vpn = 0
opener = None
robot = False
url_base = 'https://scholar.google.com'
driver = None
prev_ip = ''

user_agent = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36',
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


# get bibtex info for one paper
def search_citation(title):
  search_url = 'https://scholar.google.com/scholar?hl=en&q='+urllib.quote(title.encode('utf8'))
  print search_url
  global opener
  global robot
  driver.get(search_url)
  if opener is None:
    cj = cookielib.LWPCookieJar()
    handler = ul.HTTPCookieProcessor(cj)
    opener = ul.build_opener(handler, ul.HTTPHandler())
    #proxy = ul.ProxyHandler({'http': '142.1.97.147:80'})
    #opener = ul.build_opener(proxy)
    #ul.install_opener(opener)
  header = {'user-agent': user_agent[random.randint(0,len(user_agent)-1)],'method':'GET','referer':'https://scholar.google.com'}
  try:
    req = ul.Request(search_url, headers = header)
    res = opener.open(req).read()
  except Exception, e:
    print colored(e, 'red')
    if '503' in str(e):
      robot = True
      print colored('*****robot*****', 'red')
    ptline()
    return None
  if 'Please show you\'re not a robot' in res:
    robot = True
    print colored('*****robot*****', 'red')
    ptline()
    return None
  robot = False
  try:
    dom = bs(res,'lxml')
    # search result for title
    search_res = dom.find_all(attrs={'class':'gs_r'})
    if len(search_res) == 0:
      if ('No pages were found' not in res) and ('did not match any articles' not in res):
        robot = True
        ptline()
        return None
      # paper not found
      print colored('Paper not found: {}'.format(title),'magenta')
      return False
    gsr = search_res[0]
    title_elem = gsr.find_all(lambda x: x.name == 'h3' and x.get('class') == ['gs_rt'])[0]
    try:
      title_link = (title_elem.find_all('a'))[0]
      rtitle = title_link.text
    except Exception:
      rtitle = innermost(title_elem,[],0,1)
      rtitle = rtitle[0]
    if rtitle is None:
      ptline()
      return None
    rtitle = rtitle.strip()
    print colored("Found: "+rtitle,'green')
    try:
      title.decode('ascii')
    except UnicodeDecodeError:
      match = True
    else:
      match = check(title,rtitle)
    # paper not found
    if not match:
      print colored('title mismatch:\n\t{}\n\t{}'.format(title, rtitle), 'magenta')
      return False
    try:
      btn = driver.find_element_by_xpath("//div[@class='gs_ri'][1]//div[@class='gs_fl'][1]/a[@aria-controls='gs_cit'][1]")
      btn.click()
      texbtn = driver.find_element_by_xpath("//div[@id='gs_citi'][1]//a[@class='gs_citi'][1]")
      btnname = texbtn.text
      # no bibtex info available
      if btnname!='BibTeX':
        return False
      texurl = texbtn.get_attribute('href')
      #time.sleep(1)
      closebtn = driver.find_element_by_id('gs_cit-x')
      closebtn.click()
    except Exception:
      return False
    texreq = ul.Request(texurl, headers = header)
    texres = opener.open(texreq).read()
    return texres
  except Exception, e:
    print colored(e, 'red')
    ptline()
    return False

def parse_authors(author_str):
  try:
    author_list = author_str.split('and')
    author_list = [a.strip() for a in author_list]
    authors = []
    for a in author_list:
      if ',' in a:
        name = ' '.join((a.split(',')[::-1]))
      else:
        name = a
      authors.append(name)
    return authors
  except Exception:
    return []

def get_tex(title):
  tex = search_citation(title)
  if tex is None:
    ptline()
    return None
  if not tex:
    return False
  try:
    tex_obj = bibtexparser.loads(tex)
    tex_dict = tex_obj.entries_dict.values()[0]
    authors = parse_authors(tex_dict['author'])
    tex_dict['author'] = authors
    return tex_dict
  except Exception:
    return False
 
  
def reconnect():
  global driver
  global robot
  global prev_ip
  robot = False
  if driver:
    driver.quit()
    driver = None
  new_ip = prev_ip
  while new_ip == prev_ip:
    os.system('/opt/cisco/anyconnect/bin/vpn -s disconnect > /dev/null 2>&1')
    os.system('echo "2\n{}\n{}\n" | /opt/cisco/anyconnect/bin/vpn -s connect vpn.cites.illinois.edu > /dev/null 2>&1'.format(sys.argv[3], sys.argv[4]))
    new_ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
  prev_ip = new_ip
  print colored(new_ip,'cyan')
  #time.sleep(random.randint(5,10))
  time.sleep(1)
  if not driver:
    driver = webdriver.Firefox()
    driver.implicitly_wait(25)

      
def main():
  global driver
  outfilename = sys.argv[2]
  while os.path.exists(outfilename):
    if len(open(outfilename,'r').read())<5:
      break
    if len(outfilename.split('.')) == 2:
      outfilename = '{}.{}'.format(outfilename,1)
    else:
      i = outfilename.split('.')[2]
      new_i = str(int(i)+1)
      outfilename = outfilename.replace(i,new_i)
  papers = json.load(open(sys.argv[1], 'r'))
  global robot
  with codecs.open(outfilename,'w',encoding='utf-8') as outfile:
    outfile.write('[')
    for paper in papers:
      citations = paper['Cited by']
      for i, citation in enumerate(citations):
        ctitle = citation['title']
        info = get_tex(ctitle)
        fail = 0
        while info is None:
          fail += 1
          if fail == 10:
            time.sleep(10)
            fail = 0
          robot = True
          reconnect()
          info = get_tex(ctitle)
        fail = 0
        citation['info'] = info or {}
        citations[i] = citation
      paper['Cited by'] = citations
      json.dump(paper,outfile,indent=4,ensure_ascii=False)
      outfile.write(',\n')
    outfile.write(']')
  

def test(title):
  get_tex(title)



if __name__ == '__main__':
  if len(sys.argv)<4:
    print 'usage: python citations.py [citationfile] [outfile] [netid] [password]'
    #test('Permutation-based elitist genetic algorithm for optimization of large-sized resource-constrained project scheduling')
    exit(0)
  display = Display(visible=0, size=(800, 600))
  display.start()
  global driver
  driver=webdriver.Firefox()
  driver.implicitly_wait(25)
  main()
  driver.quit()
  driver = None
  display.stop()
  #testmain('Identifying attractive research fields for new scientists')


