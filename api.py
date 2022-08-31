from clients import GoogleMapsClient, SerpApiClient
from kw_extraction import KwExtraction
from flask import Flask, request
from flask_restx import Api, Resource, fields, reqparse

app = Flask(__name__)
api = Api(app, version='1.0', title='Date Place Keywords Extraction API',
    description='Used for extracting keywords and their occurrence count from any restaurant',    
)

@api.route('/extract/<string:query>')
@api.doc(params={'query': 'A query string (restaurant name) in string format'})
class KwExtractionApi(Resource):
    """ Flask REST API class for the web application"""

    def get(self, query:str):
        # parser = reqparse.RequestParser()
        # parser.add_argument('name', type=str)
        # parser.add_argument('custom_kws', action='split')
        # args = parser.parse_args()

        # Call SerpApiClient to get review object
        serp_api_client = SerpApiClient()
        reviews = serp_api_client.all_reviews(query, MAX_PAGE_LIMIT=5)
        
        # Pass the reviews into extraction class to extract & count key words
        custom_kws = ['quite', 'intimate', 'dim', 'waygu'] # to be implemented in FE down the road
        kw_extraction = KwExtraction(custom_kws=custom_kws)
        kws_cnt = kw_extraction.extract_kw(n_gram_range=(1,1), top_n=10, diversity=0.5)

        return kws_cnt

if __name__=='__main__':
    app.run(debug=True) # NEVER BE USED IN A PROD ENV!