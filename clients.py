from dotenv import dotenv_values
import requests
from urllib.parse import urlencode, urlparse, urlsplit, parse_qsl
from serpapi import GoogleSearch
from http import client
from typing import List
import json

# Loading environmental variables
config = dotenv_values('.env')
GOOGLE_API_KEY = config['GOOGLE_MAPS_API_KEY']
SERPAPI_KEY = config['SERPAPI_KEY']


class GoogleMapsClient(object):
    ''' Custom client class to interact with Google Maps Place API'''
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

        endpoint = f'https://maps.googleapis.com/maps/api/geocode/{self.data_type}'
        params = {'address': loc_query, 'key': self.api_key}
        url_params = urlencode(params)
        url = f'{endpoint}?{url_params}'
        r = requests.get(url)
        if r.status_code not in range(200, 299): 
            return {}

        latlng = {}
        try:
            latlng = r.json()['results'][0]['geometry']['location']
        except Exception as error:
            print(error)
        lat,lng = latlng.get('lat'), latlng.get('lng')

        return lat, lng


class SerpApiClient(object):
    ''' Custom client class to interact with SerpAPI '''
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
        ''' Search place based on query string return the first matched json
        object (including data_id that will be used in review API) '''

        if loc_query == None:
            raise Exception('SerpAPI search(): query is None type')
        # GPS coordinates of location where you want your q (query) to be applied.
        ll = f'@{self.lat},{self.lon},{self.zoom}'

        params = {
            'engine': 'google_maps',
            'q': loc_query,
            'll': ll,
            'type': 'search',
            'api_key': self.api_key,
            'hl': 'en'
        }

        search = GoogleSearch(params)
        r = search.get_dict()
        local_result = {}
        if r['search_metadata']['status'] == 'Success':
            if 'local_results' in r:
                # Local search mode is on (returning a list of local candidates e.g. MacDonald's)
                # Only take the first search result (assuming search is accurate)
                local_result = r['local_results'][0]
            elif 'place_results' in r:
                # "Showing results for type: "place" instead of type: "search" (returning only one result e.g. The Butcher Chef)
                local_result = r['place_results']
            else:
                raise Exception('SerpAPI.search(): SerpAPI search result key error: missing both local_results and place_results')
        
        return local_result


    def reviews(self, loc_query:str=None) -> dict:
        '''
        Take a location as input. Call SerpGoogleAPI to get data ID,
        then use it to return 10 user reviews and topics
        '''

        if loc_query == None:
            raise Exception('SerpAPI.reviews(): loc_query is None type')

        # Get first matched restaurant result (assuming query is always accurate
        # for now) and extract data_id
        local_result = self.search(loc_query=loc_query)
        try:
            data_id = local_result['data_id']
        except:
            print('reviews(): Empty local_result returned by search(). Terminating')
            return {}

        params = {
            'engine': 'google_maps_reviews',
            'data_id': data_id,
            'api_key': self.api_key
        }

        search = GoogleSearch(params)
        r = search.get_dict()

        # Return all responses including place_info, topics, reviews, etc
        return r

    def all_reviews(self, loc_query:str=None, MAX_PAGE_LIMIT:int=10000000) -> dict:
        '''
        Take a location as input. Call SerpGoogleAPI to get data ID, then return
        ALL the reviews using the pagination token

        MAX_PAGE_LIMIT: stop querying after review page > MAX_PAGE_LIMIT to avoid overcalling API
        '''

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
            'api_key': self.api_key,                   # your api key
            'engine': 'google_maps_reviews',                    # serpapi search engine
            'hl': 'en',                                         # language of the search
            'data_id': data_id  # place id data located inside Google Maps Place URL: located inside `data=` query parameter. 
        }

        search = GoogleSearch(params)

        reviews = [] # store ALL the reviews
        results = search.get_dict()
        place_info = results.get('place_info', []) # title, address, rating, and total review count
        topics = results.get('topics', []) # keywords and mentions (Google's version of KW extraction)

        page_num = 0
        while True:
            page_num += 1
            results = search.get_dict()

            print(f'Extracting reviews from {page_num} page.')

            if not 'error' in results:
                for result in results.get('reviews', []): # return an empty list [] if no reviews from the place
                    reviews.append({
                        # Using .get() to access dict as better practice
                        'page': page_num,
                        'name': result.get('user').get('name'),
                        'link': result.get('user').get('link'),
                        'thumbnail': result.get('user').get('thumbnail'),
                        'usr_review_cnt': result.get('user').get('reviews'),
                        'usr_photo_cnt': result.get('user').get('photos'),
                        'rating': result.get('rating'),
                        'date': result.get('date'),
                        'snippet': result.get('snippet'),
                        'images': result.get('images'),
                        'local_guide': result.get('user').get('local_guide'),
                        # other data fields (reference the-butcher-chef.json)
                    })
            else:
                print(results['error'])
                break

            if page_num > MAX_PAGE_LIMIT:
                break

            if results.get('serpapi_pagination').get('next') and results.get('serpapi_pagination').get('next_page_token'):
                # split URL in parts as a dict and update search 'params' variable to a new page that will be passed to GoogleSearch()
                search.params_dict.update(dict(parse_qsl(urlsplit(results['serpapi_pagination']['next']).query)))
            else:
                break

        # print(json.dumps(reviews, indent=4, ensure_ascii=False))
        return {'place_info': place_info, 'topics': topics, 'reviews': reviews}



    
if __name__=='__main__':
    # Config params:
    client_loc = '25 Telegram Mews'                         # User home address or current location to help scope down
    restaurant = 'MacDonald'                         # Restaurant name to search for
    prefix = 'macdonald'                                      # Prefix used for creating json file
    MAX_PAGE_LIMIT = 1000

    # Instantiate a class object
    serp = SerpApiClient(api_key=SERPAPI_KEY, client_loc=client_loc)

    # Get the entire json response from Serp Review API for future testing
    res = serp.all_reviews(loc_query=restaurant, MAX_PAGE_LIMIT=MAX_PAGE_LIMIT)

    # Directly save into json file from dictionary
    for k, v in res.items():
        with open(f'{prefix}-{k}.json', 'w') as outfile:
            json.dump(v, outfile)



