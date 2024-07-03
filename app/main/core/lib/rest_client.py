from typing import Dict, Tuple


class RestClient:
    def get(self, url, headers) -> Tuple[Dict, int]:
        raise Exception("You must implement this method in a subclass.")

    def post(self, url, headers, data) -> Tuple[Dict, int]:
        raise Exception("You must implement this method in a subclass.")

    def delete(self, url, headers) -> Tuple[Dict, int]:
        raise Exception("You must implement this method in a subclass.")

    def patch(self, url, headers, data) -> Tuple[Dict, int]:
        raise Exception("You must implement this method in a subclass.")
