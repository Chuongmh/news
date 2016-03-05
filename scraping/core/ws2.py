import threading
import urllib
from urlparse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
import sys
import re
import time
import datetime


class ws:
    tocrawl = set([])
    crawled = set([])
    counter = 0
    depth = 0

    def __init__(self, url, depth):
        self.tocrawl.add(url)
        self.depth = depth
        self.crawled = set([])
        self.counter = 0

    def update(self, links):
        if links is not None:
            for link in links:
                if link not in self.crawled:
                    self.tocrawl.add(link)
        # print("update %d" % len(self.tocrawl))

    def getLinks(self, crawling):
        self.crawled.add(crawling)
        try:
            html = urllib.urlopen(crawling)
        except:
            print("URL Open error: {}".format(sys.exc_info()))

        # print("Crawled len: %d" % len(self.crawled))
        try:
            bsObj = BeautifulSoup(html)
            links = bsObj.findAll("a", href=re.compile("(?! mailto)$"))
            tmp = set()
            for link in links:
                new_url = urljoin(crawling, link.attrs['href'])
                t = list(urlparse(new_url))
                t[3:6] = ['', '', '']
                new_url = urlunparse(t)
                if (urlparse(new_url).netloc.find(urlparse(crawling).netloc)) != -1:
                    tmp.add(new_url)
            self.counter += 1
            # print("Links len: %d" % len(links))
            self.update(tmp)
        except:
            print("getLinks error: %s" % sys.exc_info())
            return None

    def crawl(self):
        try:
            print("%d threads running" % threading.activeCount())
            crawling = self.tocrawl.pop()
            #print("Crawling: %s" % crawling)
            # print(len(self.crawled))
            self.getLinks(crawling)
        except:
            print("Crawl error: {}".format(sys.exc_info()))
            return None


    def dispatcher(self):
        # print("In Dispatcher: %s" % len(self.tocrawl))
        # while self.counter < self.depth:
        while len(self.crawled) < 50:
            T = threading.Thread(target=self.crawl())
            T.start()
            #time.sleep(1)

print("Start: {0}".format(datetime.datetime.now()))
mysite = ws("http://vnexpress.net", 2)
# print("pop: %s" % mysite.tocrawl.pop())
mysite.dispatcher()
print("Crawled: %d" % len(mysite.crawled))
#print(mysite.crawled)
print("End: {0}".format(datetime.datetime.now()))