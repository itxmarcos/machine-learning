from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime
import random
import re

"""
Wikipedia is full of sidebar, footer, and header links that appear on every page, along with links to the category pages, talk pages, and other pages that do not contain different articles.
However, if you examine the links that point to article pages (as opposed to other internal pages), they all have three things in common:
    * They reside within the div with the id set to bodyContent
    * The URLs do not contain colons
    * The URLs begin with /wiki/
The function getLinks takes in a Wikipedia article URL and returns a list of all linked article URLs in the same form.
"""

random.seed(datetime.datetime.now()) # Ensures a new random path through Wikipedia articles every time the program is run.
def getLinks(articleUrl):
    html = urlopen(f"http://en.wikipedia.org{articleUrl}")
    bsObj = BeautifulSoup(html)
    return bsObj.find("div", {"id":"bodyContent"}).findAll("a", 
                     href=re.compile("^(/wiki/)((?!:).)*$"))
links = getLinks("/wiki/Kevin_Bacon")
while len(links) > 0:
    newArticle = links[random.randint(0, len(links)-1)].attrs["href"]
    print(newArticle)
    links = getLinks(newArticle)