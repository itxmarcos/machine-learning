"""
Import "similar_wines{date}.csv" file into InfluxDB 2.0
"""

from collections import OrderedDict
from csv import DictReader
import time, argparse
import reactivex as rx
from reactivex import operators as ops
from influxdb_client import Point, InfluxDBClient, WriteOptions

parser = argparse.ArgumentParser()
parser.add_argument('--date', default=time.strftime("%Y-%m-%d"), action='store', type=str, help='Type date in format YYYY-MM-DD')
args = parser.parse_args()
date = args.date
filename = f"../dataset/{date}/similar_wines{date}.csv"

def parse_row(row: OrderedDict):
    """
    Parse row of CSV file into Point
        param row: the row of CSV file
        return: Parsed csv row to [Point]
    """
    return Point("similar_wines") \
        .tag("type", filename) \
        .field("winery", row['winery']) \
        .field("location", row['location']) \
        .field("country", row['country']) \
        .field("name", row['name']) \
        .field("color", row['color']) \
        .field("variety", row['variety']) \
        .field("price", float(row['price'])) \
        .field("rating", float(row['rating'])) \
        .field("body", float(row['body'])) \
        .field("acidity", float(row['acidity'])) \
        .field("alcohol_percentage", float(row['alcohol_percentage'])) \
        .field("editors_choice", row['editors_choice']) \
        .field("id", row['id']) \
        .field("wine_review_link", row['wine_review_link']) \
        .field("wine_review_publish_date", row['wine_review_publish_date']) \
        .field("source", row['source']) \
        .field("name_winery_ontology", row['name_winery_ontology']) \
        .field("url_winery_ontology", row['url_winery_ontology']) \
        .field("name_ontology", row['name_ontology']) \
        .field("url_wine_ontology", row['url_wine_ontology']) \
        .time(row["crawler_day"], WriteOptions.ISO8601)

"""
Convert similar_wines{date}.csv into sequence of data point
"""
data = rx \
    .from_iterable(DictReader(open(filename, 'r'))) \
    .pipe(ops.map(lambda row: parse_row(row)))

with InfluxDBClient(url="http://localhost:8086", token="D1vjfVZ8ab5McX8h_oen4T1YNEWVpushfTRRzdpLab7Q2EuLCU290s3dW8M56HC8mGNXHaatpBSDJtyg2LvMyA==", org="ITA", debug=True) as client:

    """
    Create client that writes data in batches with 50_000 items.
    """
    with client.write_api(write_options=WriteOptions(batch_size=50_000, flush_interval=10_000)) as write_api:

        """
        Write data into InfluxDB
        """
        write_api.write(bucket="PolicyCloud", record=data)

    """
    Querying max value of CBOE Volatility Index
    """
    query = 'from(bucket:"PolicyCloud")' \
            ' |> range(start: 0, stop: now())' \
            ' |> filter(fn: (r) => r._measurement == "similar_wines")' \
            ' |> max()'
    result = client.query_api().query(query=query)

    """
    Processing results
    """
    print()
    print("=== results ===")
    print()
    for table in result:
        for record in table.records:
            print('max {0:5} = {1}'.format(record.get_field(), record.get_value()))