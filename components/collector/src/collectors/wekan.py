"""Wekan metric collector."""

import requests

from ..collector import Collector
from ..type import Units, URL, Value


class WekanIssues(Collector):
    """Collector to get issues (cards) from Wekan."""

    def landing_url(self, response: requests.Response, **parameters) -> URL:
        api_url = self.api_url(**parameters)
        headers = dict(Authorization=f"Bearer {response.json()['token']}")
        board_id = self.board_id(api_url, headers, **parameters)
        return URL(f"{api_url}/b/{board_id}")

    def get_source_response(self, api_url: URL, **parameters) -> requests.Response:
        """Override because we want to do a post request to login."""
        credentials = dict(username=parameters.get("username"), password=parameters.get("password"))
        return requests.post(api_url + "/users/login", data=credentials, timeout=self.TIMEOUT)

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len(self.parse_source_response_units(response, **parameters)))

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        headers = dict(Authorization=f"Bearer {response.json()['token']}")
        api_url = self.api_url(**parameters)
        board_id = self.board_id(api_url, headers, **parameters)
        return self.get_units(api_url, board_id, headers, **parameters)

    def get_units(self, api_url, board_id, headers, **parameters) -> Units:
        """Convert the cards to units."""
        board_url = f"{api_url}/api/boards/{board_id}"
        board_slug = requests.get(board_url, timeout=self.TIMEOUT, headers=headers).json()["slug"]
        lists_url = f"{board_url}/lists"
        lists_to_ignore = parameters.get("lists_to_ignore") or []
        units: Units = []
        for card_list in requests.get(lists_url, timeout=self.TIMEOUT, headers=headers).json():
            if bool((card_list["_id"] in lists_to_ignore) or (card_list["title"] in lists_to_ignore)):
                continue
            cards_url = f"{lists_url}/{card_list['_id']}/cards"
            cards = requests.get(cards_url, timeout=self.TIMEOUT, headers=headers).json()
            units.extend(dict(key=card["_id"], url=f"{api_url}/b/{board_id}/{board_slug}/{card['_id']}",
                              list=card_list["title"], title=card["title"]) for card in cards)
        return units

    def board_id(self, api_url, headers, **parameters) -> str:
        """Return the id of the board specified by the user."""
        user_url = f"{api_url}/api/user"
        user_id = requests.get(user_url, timeout=self.TIMEOUT, headers=headers).json()["_id"]
        boards_url = f"{api_url}/api/users/{user_id}/boards"
        boards = requests.get(boards_url, timeout=self.TIMEOUT, headers=headers).json()
        return [board for board in boards if parameters.get("board") in board.values()][0]["_id"]
