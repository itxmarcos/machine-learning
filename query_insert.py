from cProfile import label
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
# from prometheus_client.exposition import basic_auth_handler
import pandas as pd
import datetime

# def my_auth_handler(url, method, timeout, headers, data):
#     username = 'foobar'
#     password = 'secret123'
#     return basic_auth_handler(url, method, timeout, headers, data, username, password)

def get_timestamp(crawler_day):
    date = datetime.datetime.strptime(crawler_day, "%Y-%m-%d")
    return datetime.datetime.timestamp(date)

df = pd.read_csv('similar_wines2022-09-27.csv')
registry = CollectorRegistry()
wine_gauge = Gauge('wine', 'wine documentation', registry=registry, labelnames= ["winery", "location", "country", "name", "color", "variety", "rating", "body", "acidity", "alcohol_percentage", "editors_choice", "id", "wine_review_link", "wine_review_publish_date", "source", "name_winery_ontology", "url_winery_ontology", "name_ontology", "url_wine_ontology"])

for index, row in df.iterrows():
    # Create dataset metrics
    winery = row['winery']
    location = row['location']
    country = row['country']
    name = row['name']
    color = row['color']
    variety = row['variety']
    price = row['price']
    rating = row['rating']
    body = row['body']
    acidity = row['acidity']
    crawler_day = get_timestamp(row['crawler_day'])
    alcohol_percentage = row['alcohol_percentage']
    editors_choice = row['editors_choice']
    id = row['id']
    wine_review_link = row['wine_review_link']
    wine_review_publish_date = row['wine_review_publish_date']
    source = row['source']
    name_winery_ontology = row['name_winery_ontology'] 
    url_winery_ontology = row['url_winery_ontology']
    name_ontology = row['name_ontology']
    url_wine_ontology = row['url_wine_ontology']

    my_dic = {"winery":winery ,"location":location, "country":country, "name":name, "color":color, "variety":variety, "rating":rating, "body":body, "acidity":acidity, "alcohol_percentage":alcohol_percentage, "editors_choice":editors_choice, "id":id, "wine_review_link":wine_review_link, "wine_review_publish_date":wine_review_publish_date, "source":source, "name_winery_ontology":name_winery_ontology, "url_winery_ontology":url_winery_ontology, "name_ontology":name_ontology, "url_wine_ontology":url_wine_ontology}
    wine_gauge.labels(**my_dic).set(crawler_day)

    push_to_gateway('localhost:9091', job='batchA', registry=registry) #handler=my_auth_handler #Push to Prometheus
