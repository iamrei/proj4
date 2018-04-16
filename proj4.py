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
from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go
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

## yelp search terms 
# DEFAULT_TERM = 'lunch'
# DEFAULT_LOCATION = 'Ann Arbor, MI'
# DEFAULT_TERM = user_inpt_term
# DEFAULT_LOCATION = user_inpt_location

SEARCH_LIMIT = 50
offset_val = 51


#get search results 1-50
def search(api_key, term, location):
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return request_1(baseurl, SEARCH_PATH, api_key, url_params=url_params)

#get search results 51-100
def search_2(api_key, term, location):
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT,
        'offset' : offset_val
    }
    return request_2(baseurl, SEARCH_PATH, api_key, url_params=url_params)

def request_1(host, path, api_key, url_params=None):
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }
    print(u'Querying {0} ...'.format(url))
    response = requests.request('GET', url, headers=headers, params=url_params)
    json_obj = response.json()
    return write_to_cache_file_1(json_obj)

def request_2(host, path, api_key, url_params=None):
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }
    print(u'Querying {0} ...'.format(url))
    response = requests.request('GET', url, headers=headers, params=url_params)
    json_obj = response.json()
    return write_to_cache_file_2(json_obj)    

def write_to_cache_file_1(json_obj):
    with open(CACHE_FNAME_1, 'w') as outfile:
        json.dump(json_obj, outfile)
    print('write_to_cache_file')    
    try:
        cache_file = open(CACHE_FNAME_1, 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION_1 = json.loads(cache_contents)
        cache_file.close()   
        return insert_to_yelp(CACHE_DICTION_1) 
    except:
        CACHE_DICTION_1 = {}  
        return insert_to_yelp(CACHE_DICTION_1)  
        

def write_to_cache_file_2(json_obj):
    with open(CACHE_FNAME_2, 'w') as outfile:
        json.dump(json_obj, outfile)
    print('write_to_cache_file')    
    try:
        cache_file = open(CACHE_FNAME_1, 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION_1 = json.loads(cache_contents)
        cache_file.close()       
        return insert_to_yelp(CACHE_DICTION_2) 
    except:
        CACHE_DICTION_1 = {}  
        return insert_to_yelp(CACHE_DICTION_2)  

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

def insert_to_yelp(CACHE_DICTION):
    yelp_results = CACHE_DICTION["businesses"] 

    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    for dic in yelp_results:
        # print(dic) 

        name = dic['name']
        website_url = dic['url']
        rating = dic['rating']
        city = dic['location']['city']
        state = dic['location']['state']    
        lat = dic['coordinates']['latitude']
        lng = dic['coordinates']['longitude']
        # print(name)
        cur.execute("INSERT INTO 'Yelp' VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", (dic['name'], dic['url'], dic['rating'], dic['location']['city'], dic['location']['state'], dic['coordinates']['latitude'], dic['coordinates']['longitude']))

    con.commit()
    print('insert successful')
    con.close()


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
baseurl_t = 'https://www.tripadvisor.com/Restaurants-g29556-Ann_Arbor_Michigan'

# get data from tripadvisor
def get_sites_data(baseurl_t):
    homepage_text = make_request_using_cache(baseurl_t)
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
        rating_trip = item.find('span')['alt'].strip().replace('of 5 bubbles', '')
        # print(rating_trip)
        # print('-'*20, '\n')
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

        
get_sites_data(baseurl_t)

## pie chart for cuisine type
def plot_piechart_cuisine():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    pie_cuisine_statement = '''SELECT Cuisine, Count(*) From Tripadvisor 
    Group by Cuisine'''

    cur.execute(pie_cuisine_statement)
    con.commit()

    lst_cuisine_type = []
    lst_cuisine_val = []
    for row in cur:
        # print(row[0], row[1])
        lst_cuisine_type.append(row[0])
        lst_cuisine_val.append(row[1])

    # print(lst_cuisine_type)
    # print(lst_cuisine_val)

    ## pie chart for cuisine types in A2
    labels = lst_cuisine_type
    values = lst_cuisine_val
    trace = go.Pie(labels=labels, values=values)
    py.plot([trace], filename='pie_chart_cuisine_tripadvisor')

# plot_piechart_cuisine()

def plot_barchart_cuisine():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    pie_cuisine_statement = '''SELECT Cuisine, Count(*) From Tripadvisor 
    Group by Cuisine'''

    cur.execute(pie_cuisine_statement)
    con.commit()

    lst_cuisine_type = []
    lst_cuisine_val = []
    for row in cur:
        # print(row[0], row[1])
        lst_cuisine_type.append(row[0])
        lst_cuisine_val.append(row[1])

    # print(lst_cuisine_type)
    # print(lst_cuisine_val)

    data = [go.Bar(
                x=lst_cuisine_type,
                y=lst_cuisine_val
        )]

    py.plot(data, filename='basic-bar')

# plot_barchart_cuisine()

## plot gauez chart for ratings 
def plot_gauzechart_rating(lst_ratings):
    scales = ['<b>Trip-<br>advisor</b>', '<b>Yelp</b>']
    scale1 = ['Very<br> Unsatisfied ',
              'Unatisfied ', 'Neutral ',
              'Satisfied ', 'Very <br> Satisfied ']
    scale2 = ['Very<br> Unsatisfied ',
              'Unatisfied ', 'Neutral ',
              'Satisfied ', 'Very <br> Satisfied ']

    scale_labels = [scale1, scale2]

    # Add Scale Titles to the Plot
    traces = []
    for i in range(len(scales)):
        traces.append(go.Scatter(
            x=[0.6], # Pad the title - a longer scale title would need a higher value 
            y=[6.25],
            text=scales[i],
            mode='text',
            hoverinfo='none',
            showlegend=False,
            xaxis='x'+str(i+1),
            yaxis='y'+str(i+1)
        ))

    # Create Scales
    ## Since we have 7 lables, the scale will range from 0-6
    shapes = []
    for i in range(len(scales)):
        shapes.append({'type': 'rect',
                       'x0': .02, 'x1': 1.02,
                       'y0': 0, 'y1': 5,
                       'xref':'x'+str(i+1), 'yref':'y'+str(i+1)})

    x_domains = [[0, .25], [.25, .5]] # Split for 4 scales
    chart_width = 800

    # Define X-Axes
    xaxes = []
    for i in range(len(scales)):
        xaxes.append({'domain': x_domains[i], 'range':[0, 4],
                      'showgrid': False, 'showline': False,
                      'zeroline': False, 'showticklabels': False})

    # Define Y-Axes (and set scale labels)
    ## ticklen is used to create the segments of the scale,
    ## for more information see: https://plot.ly/python/reference/#layout-yaxis-ticklen
    yaxes = []
    for i in range(len(scales)):
        yaxes.append({'anchor':'x'+str(i+1), 'range':[-.5,6.5],
                      'showgrid': False, 'showline': False, 'zeroline': False,
                      'ticks':'inside', 'ticklen': chart_width/20,
                      'ticktext':scale_labels[i], 'tickvals':[0., 1., 2., 3., 4.]
                     })

    # Put all elements of the layout together
    layout = {'shapes': shapes,
              'xaxis1': xaxes[0],
              'xaxis2': xaxes[1],

              'yaxis1': yaxes[0],
              'yaxis2': yaxes[1],

              'autosize': False,
              'width': chart_width,
              'height': 600
    }


    ratings = lst_ratings ## add rating data ## function 

    for i in range(len(ratings)):
        traces.append(go.Scatter(
                x=[0.5], y=ratings[i],
                xaxis='x'+str(i+1), yaxis='y'+str(i+1),
                mode='marker', marker={'size': 16, 'color': '#29ABD6'},
                text=ratings[i], hoverinfo='text', showlegend=False
        ))


    fig = dict(data=traces, layout=layout)
    py.plot(fig, filename='linear-gauge-layout')

# plot_gauzechart_rating()

## Get Yelp search results and select one of the restaurant for gauze chart
def pick_from_yelp_results():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    list_restaurant_statement = '''
    SELECT Id, RestaurantName, Rating From Yelp LIMIT 12'''

    cur.execute(list_restaurant_statement)
    con.commit()

    print('\n[Top 12 Restaurants and ratings in A2]')
    lst_restaurant_id = []
    lst_restaurant_name = []
    lst_restaurant_rating = []
    for row in cur:
        print(row[0], row[1], row[2])
        lst_restaurant_id.append(row[0])
        lst_restaurant_name.append(row[1])
        lst_restaurant_rating.append(row[2])

    question = input("Select the restaurant (number only) to compare ratings:")
    # print(question)
    restaurant_name = lst_restaurant_name[int(question)-1]
    restaurant_rating = lst_restaurant_rating[int(question)-1]
    print(lst_restaurant_name[int(question)-1])
    print(lst_restaurant_rating[int(question)-1])

    return get_from_trip_results(restaurant_name, restaurant_rating) 

# print(pick_from_yelp_results())


## Get restaurant rating from Yelp search results 
def get_from_trip_results(restaurant_name, restaurant_rating):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    find_selected_restaurant_statement = '''
    SELECT Id, RestaurantName, Rating 
    From Tripadvisor
    WHERE RestaurantName = "{}" '''

    name_check = '''
    SELECT Id, RestaurantName, Rating 
    From Tripadvisor
    WHERE RestaurantName = "{}" '''

    
    if not cur.execute(name_check.format(restaurant_name)).fetchall():  # if the table doesn't exist
        print('The selected restaurant is not found on Tripadvisor.')
        return [restaurant_rating, 0]

    else:
        cur.execute(find_selected_restaurant_statement.format(restaurant_name))
        con.commit()

        lst_ratings_two_results = []
        for row in cur:
            lst_ratings_two_results.append(restaurant_rating)
            lst_ratings_two_results.append(row[2])
            # return (row[1], row[2])
            # return (restaurant_rating, row[2])
        return plot_gauzechart_rating(lst_ratings_two_results)   

# print(pick_from_yelp_results())
# plot_gauzechart_rating(pick_from_yelp_results())

## Get Yelp search results and select one of the restaurant to locate it on the map
def pick_from_yelp_results_to_map():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    list_restaurant_statement = '''
    SELECT Id, RestaurantName, Rating From Yelp LIMIT 12 '''

    cur.execute(list_restaurant_statement)
    con.commit()

    print('\n[Top 12 Restaurants and ratings in A2]')
    lst_restaurant_id = []
    lst_restaurant_name = []
    lst_restaurant_rating = []
    for row in cur:
        print(row[0], row[1], row[2])
        lst_restaurant_id.append(row[0])
        lst_restaurant_name.append(row[1])
        lst_restaurant_rating.append(row[2])

    question = input("Select the restaurant (number only) to see on a map:")
    # print(question)
    restaurant_name = lst_restaurant_name[int(question)-1]
    restaurant_rating = lst_restaurant_rating[int(question)-1]
    print(lst_restaurant_name[int(question)-1])

    return plot_map_restaurant(restaurant_name) 

def plot_map_restaurant(restaurant_name):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    list_restaurant_location_statement = '''
    SELECT RestaurantName, Rating, Lat, Lng   
    From Yelp
    WHERE RestaurantName = "{}" '''

    cur.execute(list_restaurant_location_statement.format(restaurant_name))
    con.commit()
    
    lst_lat = []
    lst_lng = []
    lst_Name_map = []
    lst_rating_map = []

    for row in cur:
        lst_Name_map.append(row[0])
        lst_rating_map.append(str(row[1]))
        lst_lat.append(row[2])
        lst_lng.append(row[3])

    lst_show = lst_Name_map + lst_rating_map
    on_map = '-'.join(lst_show)


    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000    

    lat_vals = lst_lat
    lon_vals = lst_lng

    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
    padding = max_range * .10
    lat_axis = [min_lat - padding, max_lat + padding]
    lon_axis = [min_lon - padding, max_lon + padding]

    trace1 = dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = lst_lng,
            lat = lst_lat,
            text = on_map,
            mode = 'markers',
            marker = dict(
                size = 20,
                symbol = 'star',
                color = 'purple'
            ))

    data = [trace1]

    layout = dict(
            title = 'Restaurant in A2<br>(Hover for name and rating)',
            geo = dict(
                scope='usa',
                projection=dict( type='albers usa' ),
                showland = True,
                landcolor = "rgb(250, 250, 250)",
                subunitcolor = "rgb(100, 217, 217)",
                countrycolor = "rgb(217, 100, 217)",
                lataxis = {'range': lat_axis},
                lonaxis = {'range': lon_axis},
                center= {'lat': center_lat, 'lon': center_lon },
                countrywidth = 3,
                subunitwidth = 3
            ),
        )

    fig = dict(data=data, layout=layout )
    py.plot( fig, validate=False, filename='A2 Restaurant' )

# pick_from_yelp_results_to_map()

## make it interactive
def load_help_text():
    with open('help.txt') as f:
        return f.read()

def interactive_prompt():
    help_text = load_help_text()
    response = ''

    good_inpt_lst_0 = ['bars', 'companies', 'countries', 'regions']
    good_inpt_lst_1 = ['ratings', 'bars_sold', 'region', 'country', 'sellcountry','sourceregion', 'sellers', 'sources', 'cocoa', 'top', 'bottom' ]

    while response != 'exit':
        response = input('Enter a command: ')
        # print(response.split(' ')[0])
        # print(response.split(' ')[1])
        # print(response.split(' ')[1] in good_inpt_lst_1)

        if response == 'help':
            print(help_text)

        elif response == 'lunch' or response == 'dinner':
            user_inpt_term = response 
            response2 = input('Select a location (city, state): ')
            user_inpt_location = response2
            api_key = secrets.API_KEY
            search(api_key, user_inpt_term, user_inpt_location)
            search_2(api_key, user_inpt_term, user_inpt_location)
            pick_from_yelp_results() 

            response3 = input('Enter a command: ')
            if response3 == 'cuisine':
                response4 = input('Select a chart type for cuisines (bar/pie) : ')
                if response4 == 'bar':
                    plot_barchart_cuisine()
                    response5 = input('Select a chart type for cuisines (bar/pie) : ')
                    if response5 == 'pie':   
                        plot_piechart_cuisine()
                elif response4 == 'pie':   
                    plot_piechart_cuisine()
                    response5 = input('Select a chart type for cuisines (bar/pie) : ')
                    if response5 == 'bar':   
                        plot_barchart_cuisine()
                else:
                    print('Command not recognized:', response4)        
        elif response == 'map':
                pick_from_yelp_results_to_map()


        elif response == "exit":
            print('Bye!\n')
            break

        else:
            print('Command not recognized:', response) 

## create a unittesting file
## revise the Readme file 


if __name__ == '__main__':
    # main()
    interactive_prompt()

