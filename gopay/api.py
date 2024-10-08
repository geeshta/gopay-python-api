from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlsplit, urlunsplit

from gopay.enums import ContentType, Language
from gopay.http import ApiClient, Request, Response


@dataclass
class GoPay:
    """
    This class saves the basic configuration, sets the base_url and passes requests
    to the API Client
    """

    config: dict
    services: dict = field(default_factory=dict)
    base_url: str = field(default="", init=False)
    api_client: ApiClient = field(init=False)

    def __post_init__(self):
        # Make sure URL will be in the form of example.com/api
        urlparts = urlsplit(self.config["gateway_url"])
        self.base_url = urlunsplit((urlparts.scheme, urlparts.netloc, "/api", "", ""))
        
        # Prepare
        api_client_config = {
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "gateway_url": self.base_url,
            "scope": self.config["scope"],
        }

        # Add optional parameters if found
        if (timeout := self.config.get("timeout")) is not None:
            api_client_config.update({"timeout": timeout})

        if (logger := self.services.get("logger")) is not None:
            api_client_config.update({"logger": logger})

        if (cache := self.services.get("cache")) is not None:
            api_client_config.update({"cache": cache})


        # Create the API client
        self.api_client = ApiClient(
            **api_client_config
        )

    def call(
        self,
        method: str,
        path: str,
        content_type: ContentType | None = None,
        body: dict | None = None,
    ) -> Response:
        """
        Sets some default headers and passes requests to the API Client
        """
        # Build the request
        request = Request(
            method=method, path=path, content_type=content_type, body=body
        )

        # Add some default headers
        request.headers = {
            "Accept": "application/json",
            "User-Agent": "GoPay Python SDK",
            "Accept-Language": "cs-CZ"
            if self.config["language"] in [Language.CZECH, Language.SLOVAK]
            else "en-US",
        }
        if content_type is not None:
            request.headers["Content-Type"] = content_type

        return self.api_client.send_request(request)
