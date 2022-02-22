from urllib.request import urlopen
from bs4 import BeautifulSoup

html = urlopen("http://www.pythonscraping.com/pages/warandpeace.html")
bsObj = BeautifulSoup(html)

"""
With find() and findAll() you can easily filter HTML pages to find lists of desired tags, or a single tag, based on their various attributes.
findAll(tag, attributes, recursive, text, limit, keywords) ARGUMENTS EXPLANATION
    * tag --> you can pass a string name of a tag or even a Python list of string tag names.
        .findAll({"h1","h2","h3","h4","h5","h6"})
    * attributes --> takes a Python dictionary of attributes and matches tags that contain any one of those attributes.
        .findAll("span", {"class":{"green", "red"}})
    * recursive --> is a boolean True by default. If set to False, it will look only at the top-level tags in your document.
    * text --> it matches based on the text content of the tags, rather than properties of the tags themselves.
        nameList = bsObj.findAll(text="the prince")
        print(len(nameList))
    * limit --> if you’re only interested in retrieving the first x items from the page in the order that they occur, not necessarily the first ones that you want.
    * keywords --> select tags that contain a particular attribute, or set of attributes.
        allText = bsObj.findAll(id="title", class="text")
"""
nameList = bsObj.findAll("span", {"class":"green"})
"""
.get_text() strips all tags from the document you are working with and returns a string containing the text only.
It’s much easier to find what you’re looking for in a BeautifulSoup object than in a block of text so, 
in general, you should try to preserve the tag structure of a document as long as possible. 
"""
for name in nameList:
    print(name.get_text())