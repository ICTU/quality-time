"""Source collector base classes."""

import logging
import traceback
from urllib.parse import quote
from abc import ABC
from typing import Optional, Union, cast
import requests


from requests.models import HTTPBasicAuth, Response
from model.tracker_issue_status import TrackerIssueStatus

from server_utilities.functions import stable_traceback, tokenless
from server_utilities.type import URL


class BaseTrackerCollector(ABC):
    """Base class for tracker collectors.

    Tracker collectors are subclasses of this class that know how to collect the
    measurement data for one specific metric from one specific source.
    """

    source_type = ""  # The source type is set on the subclass, when the subclass is registered
    subclasses: set[type["BaseTrackerCollector"]] = set()

    def __init__(self, tracker, tracker_issue) -> None:
        self._tracker = tracker
        self._safe_tracker_issue = quote(tracker_issue, safe="")

    def __init_subclass__(cls) -> None:
        BaseTrackerCollector.subclasses.add(cls)
        super().__init_subclass__()

    @classmethod
    def get_subclass(cls, source_type: str) -> Optional[type["BaseTrackerCollector"]]:
        """Return the subclass registered for the source/metric name.

        First try to find a match on both source type and metric type. If no match is found, return the generic
        collector for the source type.
        """
        for subclass in cls.subclasses:
            if subclass.__name__.lower() == source_type.replace("_", ""):
                subclass.source_type = source_type
                return subclass

        logging.warning("Couldn't find trackercollector subclass for tracker type %s", source_type)
        return None

    def collect(self) -> dict:
        """Return the measurement from this source."""
        response = self.__safely_get_source_response()
        if response["error"] is not None:
            status = TrackerIssueStatus.connection_error(response["error"])
        else:
            status = self.__safely_parse_source_response(response["response"])
            status.landing_url = self.__safely_parse_landing_url()
        return status.to_dict()

    def _api_url(self) -> URL:
        """Translate the url parameter into the API url."""
        return cast(URL, self._tracker.get("url", ""))

    def __safely_get_source_response(self) -> dict:
        """Connect to the source and get the data, without failing.

        This method should not be overridden because it makes sure the collection of source data never causes the
        collector to fail.
        """
        api_url = safe_api_url = self.__class__.__name__
        response: dict[str, Optional[Union[Response, str]]] = dict(response=None, error=None)
        try:
            api_url = self._api_url()
            safe_api_url = tokenless(api_url) or self.__class__.__name__
            response["response"] = self._get_source_response(api_url)
            logging.info("Retrieved %s", safe_api_url)
        except Exception as reason:  # pylint: disable=broad-except
            response["error"] = stable_traceback(traceback.format_exc())
            logging.error("Failed to retrieve %s: %s", safe_api_url, self.__logsafe_exception(reason))
        return response

    @staticmethod
    def __logsafe_exception(exception: Exception) -> str:
        """Return a log-safe version of the exception."""
        return tokenless(str(exception)) if str(exception) else exception.__class__.__name__

    def _get_source_response(self, url: URL) -> Response:
        """Open the url(s). Can be overridden if a post request is needed or serial requests need to be made."""
        credentials = self._basic_auth_credentials()
        auth = None
        if credentials is not None:
            auth = HTTPBasicAuth(credentials[0], credentials[1])

        response = requests.get(url, auth=auth)
        return response

    def _basic_auth_credentials(self) -> Optional[tuple[str, str]]:
        """Return the basic authentication credentials, if any."""
        credentials = username, password = self._tracker["username"], self._tracker["password"]
        return credentials if username and password else None

    def __safely_parse_source_response(self, response: Response) -> TrackerIssueStatus:
        """Parse the data from the responses, without failing.

        This method should not be overridden because it makes sure that the parsing of source data never causes the
        collector to fail.
        """
        if response.status_code != 200:
            try:
                raw_message = response.json().get("errorMesssage", "")
            except Exception:  # pylint: disable=broad-except
                raw_message = ""
            error_message = (
                f"{str(response.status_code)}: {raw_message}" if raw_message else f"{str(response.status_code)}"
            )
            return TrackerIssueStatus.connection_error(error_message)
        try:
            status = self._parse_source_response(response)
        except Exception:  # pylint: disable=broad-except
            status = TrackerIssueStatus.parse_error(stable_traceback(traceback.format_exc()))
        return status

    def _parse_source_response(self, response) -> TrackerIssueStatus:
        """Parse the responses to get the measurement value, the total value, and the entities for the metric.

        This method needs to be overridden in the subclass to implement the actual
        parsing of the source responses.
        """
        raise NotImplementedError(
            "This method needs to be overridden in the subclass to "
            + "implement the actual parsing of the source responses."
        )

    def _landing_url(self) -> URL:  # pylint: disable=unused-argument
        """Return a user-friendly landing url.

        This method needs to be overridden in the subclass to implement the actual
        parsing of the url to the human-readable tracker issue.
        """
        raise NotImplementedError(
            "This method needs to be overridden in the subclass to "
            + "implement the actual parsing of the url to the human-readable tracker issue."
        )

    def __safely_parse_landing_url(self) -> URL:
        """Parse the responses to get the landing url, without failing.

        This method should not be overridden because it makes sure that the parsing of source data never causes the
        collector to fail.
        """
        try:
            return self._landing_url()
        except Exception:  # pylint: disable=broad-except
            return self._api_url()
