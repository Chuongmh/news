from urllib import urlopen
from bs4 import BeautifulSoup
import re


def getLinks(url):
    try:
        html = urlopen(url)
    except IOError:
        return None
    except:
        return None

    try:
        bsObj = BeautifulSoup(html)
        links = bsObj.findAll("a", href=re.compile("(?! mailto)$"))
        #print(len(links))
    except:
        return None
    return links

