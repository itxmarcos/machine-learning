from urllib.request import urlopen
from bs4 import BeautifulSoup

html = urlopen("http://www.pythonscraping.com/pages/page3.html")
bsObj = BeautifulSoup(html)

"""
This code prints out the list of product rows in the giftList table, including the initial row of column labels. 
If you were to write it using the descendants() function instead of the children() function, about two dozen tags 
would be found within the table and printed, including img tags, span tags, and individual td tags.
"""
for child in bsObj.find("table",{"id":"giftList"}).children:
    print(child)

"""
Objects cannot be siblings with themselves. Any time you get siblings of an object, the object itself will not be 
included in the list. As the name of the function implies, it calls next siblings only. We can select all the rows 
in the table, without selecting the title row itself.
"""
for sibling in bsObj.find("table",{"id":"giftList"}).tr.next_siblings:
    print(sibling)
"""
previous_siblings function can often be helpful if there is an easily selectable tag at the end of a list of 
sibling tags that you would like to get.
"""
print(bsObj.find("img",{"src":"../img/gifts/img1.jpg"
                       }).parent.previous_sibling.get_text())