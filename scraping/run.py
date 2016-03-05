from core import scrapetest
from vnexpress import getArticle
from time import sleep

scrapetest.run("http://vnexpress.net")
sleep(15)
getArticle.parseArticles()