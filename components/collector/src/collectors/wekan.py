"""Wekan metric collector."""

import requests

from ..collector import Collector
from ..type import URL, Value


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
        token = response.json()["token"]
        headers = dict(Authorization=f"Bearer {token}")
        api_url = self.api_url(**parameters)
        board_id = parameters.get("board")
        lists_url = f"{api_url}/api/boards/{board_id}/lists"
        lists = requests.get(lists_url, timeout=self.TIMEOUT, headers=headers).json()
        cards_urls = [f"{lists_url}/{card_list['_id']}/cards" for card_list in lists]
        nr_cards = sum([len(requests.get(url, timeout=self.TIMEOUT, headers=headers).json()) for url in cards_urls])
        return str(nr_cards)
