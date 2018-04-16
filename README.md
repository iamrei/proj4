# proj4

This program allows a user to type 1) dinner or lunch and 2) location (Ann Arbor, MI) in order to show search results from Yelp, to compare ratings with Tripadvisor and to present relevant charts and the location on a map for the selected restaurants.

The data sources:
1) Web Page
https://www.tripadvisor.com/Restaurants-g29556-Ann_Arbor_Michigan.html

2) Web API: Yelp Fusion
https://www.yelp.com/developers/documentation/v3/business_search
You will need API key to access API: get the key here (https://www.yelp.com/developers/v3/manage_app).

How code is structured:
1) class Restaurant: for names and ratings for the restaurant from the search results (Yelp/Tripadvisor)
2) key functions
search(api_key, term, location) : request data to get search results from Yelp
write_to_cache_file_1(json_obj) : cache data and create json files
init_db(db_name) : initialize sql tables
get_sites_data(baseurl_t) :  request data to get search results from Tripadvisor and cache with json
plot_XXXX_XXXXX() : plot data results
pick_from_yelp_results(): allows users to select a specific restaurant 

Commands available:
1) lunch
    Description: select dining options
    Options:
    1) city, state (e.g. Ann Arbor, MI): Specifies a city to get a list of
    restaurants from Yelp and compare the ratings of the selected
    restaurant from Tripadvisor.

2) dinner
    Description: select dining options
    Options:
    1) city, state (e.g. Ann Arbor, MI): Specifies a city to get a list of
    restaurants from Yelp and compare the ratings of the selected
    restaurant from Tripadvisor.

3) cuisine
    Description: shows available cuisine types of the selected city
    cuisine types presentation options (bar/pie): see cuisine types of
    restaurant in the city with bar/pie chart.

4) map
    Description: Lists restaurants according to the specified location
    and locate the selected restaurant on the map.

5) help
    Description: shows this document to understand how this program works.

Recommendation: select lunch/dinner > cuisine > select map to get the best results.

