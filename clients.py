from dotenv import dotenv_values
import requests
from urllib.parse import urlencode, urlparse, parse_qsl
from serpapi import GoogleSearch
from http import client
from typing import List
import json

# Loading environmental variables
config = dotenv_values(".env")
GOOGLE_API_KEY = config['GOOGLE_MAPS_API_KEY']
SERPAPI_KEY = config['SERPAPI_KEY']


class GoogleMapsClient(object):
    """ Custom client to interact with Google Maps Place API"""
    data_type = 'json'
    client_loc = None
    api_key = None

    def __init__(self, api_key:str=None, client_loc:str=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if api_key == None:
            raise Exception('Google Maps API key is missing')

        self.api_key = api_key
        self.client_loc = client_loc
    
    def extract_lat_lon(self, location=None):
        loc_query = self.client_loc
        if location != None:
            loc_query = location
        assert(loc_query != None)

        endpoint = f"https://maps.googleapis.com/maps/api/geocode/{self.data_type}"
        params = {"address": loc_query, "key": self.api_key}
        url_params = urlencode(params)
        url = f"{endpoint}?{url_params}"
        r = requests.get(url)
        if r.status_code not in range(200, 299): 
            return {}

        latlng = {}
        try:
            latlng = r.json()['results'][0]['geometry']['location']
        except Exception as error:
            print(error)
        lat,lng = latlng.get("lat"), latlng.get("lng")

        return lat, lng


class SerpApiClient(object):
    """ Custom client to interact with SerpAPI """
    lat = None
    lon = None
    data_type = 'json'
    zoom = '14z'
    client_loc = None
    api_key = None

    def __init__(self, api_key:str=None, client_loc:str=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if api_key == None:
            raise Exception('SerpAPI key is missing')

        self.api_key = api_key
        self.client_loc = client_loc

        # Extract lat, lon of client's location later used in SerpAPI Google Map search
        if self.client_loc != None:
            map_client = GoogleMapsClient(api_key=GOOGLE_API_KEY, client_loc=self.client_loc)
            self.lat, self.lon = map_client.extract_lat_lon(self.client_loc)

    def search(self, loc_query:str=None) -> dict:
        """ Search place based on query string return the first matched json
        object (including data_id that will be used in review API) """

        if loc_query == None:
            raise Exception('SerpAPI search(): query is None type')
        # GPS coordinates of location where you want your q (query) to be applied.
        ll = f'@{self.lat},{self.lon},{self.zoom}'

        params = {
            "engine": "google_maps",
            "q": loc_query,
            "ll": ll,
            "type": "search",
            "api_key": self.api_key,
            'hl': 'en'
        }

        search = GoogleSearch(params)
        r = search.get_dict()
        local_result = {}
        if r['search_metadata']['status'] == 'Success':
            # Only take the first search result (assuming search is accurate)
            local_result = r["place_results"]
        
        return local_result


    def reviews(self, loc_query:str=None) -> dict:
        """ Take a location as input. Call SerpGoogleAPI to get data ID,
        then use it to return all the user reviews and topics (future)"""

        if loc_query == None:
            raise Exception('SerpAPI reviews(): query is None type')

        # Get first matched restaurant result (assuming query is always accurate
        # for now) and extract data_id
        local_result = self.search(loc_query=loc_query)
        try:
            data_id = local_result['data_id']
        except:
            print('reviews(): Empty local_result returned by search(). Terminating')
            return {}

        params = {
            "engine": "google_maps_reviews",
            "data_id": data_id,
            "api_key": self.api_key
        }

        search = GoogleSearch(params)
        r = search.get_dict()

        # Return all responses including place_info, topics, reviews, etc
        return r


    
if __name__=='__main__':
    client_loc = '25 Telegram Mews'
    restaurant = 'The Butcher Chef'
    serp = SerpApiClient(api_key=SERPAPI_KEY, client_loc=client_loc)

    # Get the entire json response from Serp Review API for future testing
    r = serp.reviews(loc_query=restaurant)
    # Directly save into json file from dictionary
    with open('the-butcher-chef.json', 'w') as outfile:
        json.dump(r, outfile)



