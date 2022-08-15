from clients import GoogleMapsClient


class Extraction(GoogleMapsClient):
    """ Data processsing layer to process the data get from API"""

    def __init__(self, api_key: str = None, client_loc: str = None, *args, **kwargs) -> None:
        super().__init__(api_key, client_loc, *args, **kwargs)

    def extract_kw(self, reviews:List) -> dict:
        pass

    def match_kw(self, kws:dict) -> dict:
        pass
