import json
import pandas as pd
from google_scraper import GoogleScraper

# Specify the path to the JSON file
json_file_path = 'config_scraper.json'

# Read the JSON file
with open(json_file_path, 'r') as file:
    conf = json.load(file)

# Access the arguments from the JSON data
query = conf['query']
year = conf['year']

query = query.replace('YEAR', f"{year}")

res_f = f"{query}.csv"
res_f = res_f.replace(
    ' ', '').replace(
    '-', '').replace(
    'after:', '_').replace(
    'before:', '_')

search_base = "https://www.google.com/search?q="
search_query = search_base + query

# print(search_query)

gs = GoogleScraper()
gs.open_webdriver()
gs.get_pages(search_query)
gs.make_dataframe()
gs.close_webdriver()
gs.save_csv(res_f)

