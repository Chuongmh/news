import threading
import Queue
import urllib
from urllib import urlopen
from urlparse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
import hashlib
import sys
import re
import datetime

g_URLsDict = dict()


class Crawler(threading.Thread):
    global g_URLsDict
    varLock = threading.Lock()
    count = 0

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        # self.url = self.queue.get()
        # self.links = []

    def getLinks(self, url):
        try:
            html = urlopen(url)
        except IOError as err:
            print("getLinks openurl: {}".format(err.message))
            return

        try:
            bsObj = BeautifulSoup(html, "html.parser")
            links = bsObj.findAll("a", href=re.compile("(?! mailto)$"))
            tmp = []
            for link in links:
                if 'href' in link.attrs:
                    new_url = urljoin(url, link.attrs['href'])
                    t = list(urlparse(new_url))
                    t[3:6] = ['', '', '']
                    new_url = urlunparse(t)
                    if (urlparse(new_url).netloc.find(urlparse(url).netloc)) != -1:
                        tmp.append(new_url)
            return tmp
        except:
            print("getLinks BeautifulSoup: {}".format(sys.exc_info()))

    def run(self):
        while 1:
            print self.getName() + " started"
            url = self.queue.get()
            # print url
            links = self.getLinks(url)
            # print links
            # """
            for link in links:
                self.fp = hashlib.sha1(link).hexdigest()
                Crawler.varLock.acquire()
                if self.fp in g_URLsDict:
                    Crawler.varLock.release()
                else:
                    Crawler.count += 1
                    # print("Total Link: %d" % len(g_URLsDict))
                    # print link
                    g_URLsDict[self.fp] = link
                    Crawler.varLock.release()
                    if Crawler.count > 10:
                        pass
                    else:
                        self.queue.put(link)

                    # print self.getName()+ " %d"%self.queue.qsize()

            self.queue.task_done()
            # """
        # print(self.getName() + "Done While; Size: %d" % self.queue.qsize())


print("Start time: {0}".format(datetime.datetime.now()))
stime = datetime.datetime.now()
print g_URLsDict
sources = ["http://kinhdoanh.vnexpress.net/", "http://giaitri.vnexpress.net/", "http://thethao.vnexpress.net/",
          "http://suckhoe.vnexpress.net/", "http://giadinh.vnexpress.net/", "http://dulich.vnexpress.net/",
          "http://dulich.vnexpress.net/", "http://sohoa.vnexpress.net/"]
source = ["http://vnexpress.net"]

queue = Queue.Queue()

for i in range(8):
    t = Crawler(queue)
    t.setDaemon(True)
    t.start()

for s in source:
    queue.put(s)
print("Joining...")
queue.join()
print("Joining Done")

for value in g_URLsDict:
    print g_URLsDict[value]

print(len(g_URLsDict))
print("End time: {0}".format(datetime.datetime.now()))
etime = datetime.datetime.now()
tdelta = etime - stime
print(tdelta)