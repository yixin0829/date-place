from clients import GoogleMapsClient, SerpApiClient


class Extraction(object):
    """
    Data processsing class to process the data get from SerpAPI and does keywords extraction
    """

    def __init__(self, api_key: str = None, client_loc: str = None, *args, **kwargs) -> None:
        super().__init__(api_key, client_loc, *args, **kwargs)

    def process(self, res:dict=None):
        pass

    def extract_kw(self, reviews:List) -> dict:
        pass

    def match_kw(self, kws:dict) -> dict:
        pass
