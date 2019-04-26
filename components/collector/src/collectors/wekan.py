"""Wekan metric collector."""

import requests

from ..collector import Collector
from ..type import Units, URL, Value


class WekanIssues(Collector):
    """Collector to get issues (cards) from Wekan."""

    def landing_url(self, **parameters) -> URL:
        url = super().api_url(**parameters)
        return URL(f"{url}/b/{parameters.get('board')}")

    def get_source_response(self, api_url: URL, **parameters) -> requests.Response:
        """Override because we want to do a post request to login."""
        credentials = dict(username=parameters.get("username"), password=parameters.get("password"))
        return requests.post(api_url + "/users/login", data=credentials, timeout=self.TIMEOUT)

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len(self.parse_source_response_units(response, **parameters)))

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        headers = dict(Authorization=f"Bearer {response.json()['token']}")
        api_url = self.api_url(**parameters)
        board_id = parameters.get("board")
        board_url = f"{api_url}/api/boards/{board_id}"
        board_slug = requests.get(board_url, timeout=self.TIMEOUT, headers=headers).json()["slug"]
        lists_url = f"{board_url}/lists"
        lists = requests.get(lists_url, timeout=self.TIMEOUT, headers=headers).json()
        cards_urls = [f"{lists_url}/{card_list['_id']}/cards" for card_list in lists]
        units = []
        for cards_url in cards_urls:
            cards = requests.get(cards_url, timeout=self.TIMEOUT, headers=headers).json()
            units.extend(dict(key=card["_id"], url=f"{api_url}/b/{board_id}/{board_slug}/{card['_id']}",
                              title=card["title"]) for card in cards)
        return units
