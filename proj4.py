from __future__ import print_function

import argparse
import json
import pprint
import sys
import urllib
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
import plotly.plotly as py
import sqlite3
import secrets

##YELP DATA
CACHE_FNAME_1 = 'yelp_cache_file_1.json'
try:
    cache_file = open(CACHE_FNAME_1, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION_1 = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION_1 = {}

CACHE_FNAME_2 = 'yelp_cache_file_2.json'
try:
    cache_file = open(CACHE_FNAME_2, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION_2 = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION_2 = {}    

API_KEY = secrets.API_KEY
baseurl = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'


DEFAULT_TERM = 'lunch'
DEFAULT_LOCATION = 'Ann Arbor, MI'
SEARCH_LIMIT = 50
offset_val = 51


def request(host, path, api_key, url_params=None):

    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }
    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()

#get search results 1-50
def search(api_key, term, location):
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return request(baseurl, SEARCH_PATH, api_key, url_params=url_params)

#get search results 51-100
def search_2(api_key, term, location):
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT,
        'offset' : offset_val
    }
    return request(baseurl, SEARCH_PATH, api_key, url_params=url_params)


resul1 = search(API_KEY, DEFAULT_TERM, DEFAULT_LOCATION)
resul2 = search_2(API_KEY, DEFAULT_TERM, DEFAULT_LOCATION)

with open(CACHE_FNAME_1, 'w') as outfile:
    json.dump(resul1, outfile)

with open(CACHE_FNAME_2, 'w') as outfile:
    json.dump(resul2, outfile)


## SQL CREATE TABLES
DB_NAME = 'final.sqlite'

def init_db(db_name):
    try:
        con = sqlite3.connect(DB_NAME)
        print(sqlite3.version)
    except Error as e:
        print(e)
    
    table_name = "'Yelp'"
    table_check = "SELECT name FROM sqlite_master WHERE type='table' AND name={};".format(table_name)
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")


    cur.executescript("""
    DROP TABLE IF EXISTS 'Yelp'; 
    """) 

#code to create table(if not exists) goes here
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS 'Yelp' (
          'Id' INTEGER PRIMARY KEY AUTOINCREMENT, 
          'RestaurantName' TEXT, 
          'Website_url' TEXT,
          'Rating' REAL,
          'City' TEXT,
          'State' INTEGER,
          'Lat' INTEGER,
          'Lng' INTEGER,

           FOREIGN KEY ('RestaurantName') REFERENCES 'Website' ('Id')
           )
    """)
    #close database connection
    con.commit()
    con.close()

    print('DB is initiated')

init_db(DB_NAME)


## insert Yelp search results to table Yelp.
# print(CACHE_DICTION) 
# print('\n','-'*20,'\n')
yelp_results_1 = CACHE_DICTION_1["businesses"] 
yelp_results_2 = CACHE_DICTION_2["businesses"] 
# print(yelp_results)

con = sqlite3.connect(DB_NAME)
cur = con.cursor()

for dic in yelp_results_1:
    # print(dic) 
    # print(name)
    name = dic['name']
    website_url = dic['url']
    rating = dic['rating']
    city = dic['location']['city']
    state = dic['location']['state']    
    lat = dic['coordinates']['latitude']
    lng = dic['coordinates']['longitude']


    cur.execute("INSERT INTO 'Yelp' VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", (dic['name'], dic['url'], dic['rating'], dic['location']['city'], dic['location']['state'], dic['coordinates']['latitude'], dic['coordinates']['longitude']))

con.commit()

for dic in yelp_results_2:
    # print(dic) 
    # print(name)
    name = dic['name']
    website_url = dic['url']
    rating = dic['rating']
    city = dic['location']['city']
    state = dic['location']['state']    
    lat = dic['coordinates']['latitude']
    lng = dic['coordinates']['longitude']


    cur.execute("INSERT INTO 'Yelp' VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", (dic['name'], dic['url'], dic['rating'], dic['location']['city'], dic['location']['state'], dic['coordinates']['latitude'], dic['coordinates']['longitude']))

con.commit()
con.close()


CACHE_FNAME = 'webpage_cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

def get_unique_key(url):
    return url 

def make_request_using_cache(url):
    unique_ident = get_unique_key(url)

    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        print("Making a request for new data...")
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]


## create a table Tripadvisor
DB_NAME = 'final.sqlite'

def init_db(db_name):
    try:
        con = sqlite3.connect(DB_NAME)
        print(sqlite3.version)
    except Error as e:
        print(e)
    
    table_name = "'Tripadvisor'"
    table_check = "SELECT name FROM sqlite_master WHERE type='table' AND name={};".format(table_name)
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    cur.executescript("""
    DROP TABLE IF EXISTS 'Tripadvisor'; 
    """) 
 
#code to create table(if not exists) goes here
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS 'Tripadvisor' (
          'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
          'RestaurantName' TEXT, 
          'Rating' REAL,
          'ReviewCount' INTEGER,
          'Rank' TEXT,
          'Cuisine' TEXT
           )
    """)
    #close database connection
    con.commit()
    con.close()

    print('DB is initiated')

init_db(DB_NAME)


## insert Tripadvisor search results to table Yelp. 
CACHE_FNAME = 'webpage_cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

def get_unique_key(url):
    return url 

def make_request_using_cache(url):
    unique_ident = get_unique_key(url)

    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        print("Making a request for new data...")
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]


## create a table Tripadvisor
DB_NAME = 'final.sqlite'

def init_db(db_name):
    try:
        con = sqlite3.connect(DB_NAME)
        print(sqlite3.version)
    except Error as e:
        print(e)
    
    table_name = "'Tripadvisor'"
    table_check = "SELECT name FROM sqlite_master WHERE type='table' AND name={};".format(table_name)
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    cur.executescript("""
    DROP TABLE IF EXISTS 'Tripadvisor'; 
    """) 
 
#code to create table(if not exists) goes here
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS 'Tripadvisor' (
          'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
          'RestaurantName' TEXT, 
          'Rating' REAL,
          'ReviewCount' INTEGER,
          'Rank' TEXT,
          'Cuisine' TEXT
           )
    """)
    #close database connection
    con.commit()
    con.close()

    print('DB is initiated')

init_db(DB_NAME)


## insert Tripadvisor search results to table Yelp. 
con = sqlite3.connect(DB_NAME)
cur = con.cursor()
baseurl = 'https://www.tripadvisor.com/Restaurants-g29556-Ann_Arbor_Michigan'
# get data from tripadvisor
def get_sites_data(baseurl):
    # baseurl = 'https://www.tripadvisor.com/Restaurants-g29556-Ann_Arbor_Michigan'
    # second_page_url = "https://www.tripadvisor.com/RestaurantSearch-g29556-oa90-Ann_Arbor_Michigan.html#EATERY_LIST_CONTENTS"
    # # print(dict_url_for_state[state_abbr])
    # # print(second_level_page_url)
    # second_page_text = make_request_using_cache(second_page_url)

    homepage_text = make_request_using_cache(baseurl)
    # print(homepage_text)
    homepage_soup = BeautifulSoup(homepage_text, 'html.parser')
    # print(homepage_soup)

    content = homepage_soup.find('div', id='EATERY_SEARCH_RESULTS')
    lst_item = content.find_all('div', class_='ui_column is-9 shortSellDetails')
    # print(lst_item)

    lst_title = []
    lst_rating = []
    lst_review_count = []
    lst_rank = []
    lst_cuisine = []

    for item in lst_item:
         
        title_block = item.find('div', class_='title')
        title = title_block.find('a').text.strip()
        rating_trip = item.find('span')['alt'].strip().replace('bubbles', '')
        review_count = item.find('span', class_='reviewCount').text.strip().replace('reviews', '') 
        rank_trip = item.find('div', class_='popIndexBlock').text.strip()
        cuisine = item.find(class_='item cuisine').text.strip()

        # print(title)
        # print(rating_trip)
        # print(review_count)
        # print(rank_trip)
        # print(cuisine)

        lst_title.append(title)
        lst_rating.append(rating_trip)
        lst_review_count.append(rating_trip)
        lst_rank.append(rank_trip)
        lst_cuisine.append(cuisine)

# print(lst_title)
# print(len(lst_title))

        cur.execute("INSERT INTO 'Tripadvisor' VALUES (NULL, ?, ?, ?, ?, ?)", (title, rating_trip, review_count, rank_trip, cuisine))

    con.commit()
    con.close()

        
get_sites_data(baseurl)










# if __name__ == '__main__':
#     main()