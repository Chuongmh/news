from urllib import urlopen
from bs4 import BeautifulSoup
from urlparse import urlparse, urljoin, urlunparse
#from threading import Thread
from multiprocessing.pool import ThreadPool as Pool
from multiprocessing import cpu_count
import re
import sys
import datetime


class ws:
    visited = []
    urls = []
    glob_visited = []
    depth = 0
    counter = 0
    threadlist = []
    root = ""

    def __init__(self, url, depth):
        self.root = url
        self.depth = depth
        self.glob_visited.append(url)

    def scrapeStep(self, root):
        result_urls = []

        try:
            html = urlopen(root)
        except IOError as err:
            print("scrapeStep Error: {}".format(err.message))
        except Exception as err:
            print("scrapeStep Error: {}".format(err.message))

        try:
            bsObj = BeautifulSoup(html)
            links = bsObj.findAll("a", href=re.compile("(?! mailto)$"))
            for link in links:
                new_url = urljoin(root, link.attrs['href'])
                t = list(urlparse(new_url))
                # Remove params, query, fragment
                t[3:6] = ['', '', '']
                new_url = urlunparse(t)
                if (urlparse(new_url).netloc.find(urlparse(root).netloc)) != -1:
                    result_urls.append(new_url)
        except:
            print("scrapeStep Error: {}".format(sys.exc_info()))
        for res in result_urls:
            self.glob_visited.append(res)

    def run(self):
        while self.counter < self.depth:
            for w in self.glob_visited:
                if w not in self.visited:
                    self.visited.append(w)
                    self.urls.append(w)
            self.glob_visited = []
            """
            for r in self.urls:
                try:
                    t = Thread(target=self.scrapeStep, args=(r,))
                    self.threadlist.append(t)
                    t.start()
                except Exception as err:
                    print("ws.run: {}".format(err.message))
            for g in self.threadlist:
                g.join()
            """
            pool = Pool(cpu_count()*2)
            results = pool.map(self.scrapeStep, self.urls)
            self.counter+=1
        print(len(self.visited))
        return self.visited

url = "http://vnexpress.net"
print("Start: {0}".format(datetime.datetime.now()))
mysite = ws(url,2)
mysite.run()
print("End: {0}".format(datetime.datetime.now()))