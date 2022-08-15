from clients import Processing


class Api(Processing):
    """ Flask REST API class for the web application"""

    def __init__(self, api_key: str = None, client_loc: str = None, *args, **kwargs) -> None:
        super().__init__(api_key, client_loc, *args, **kwargs)

    def get_review_kws():
        pass