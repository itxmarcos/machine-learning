# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

"""
Each Scrapy Item object represents a single page on the website.
Obviously, you can define as many fields as you’d like (url, content, header image, etc.),
but I’m simply collecting the title field from each page, for now.
"""

class Article(Item):
    # define the fields for your item here like:
    title = Field()
