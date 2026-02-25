"""HTTP base client for OpenDerisk API."""

import json
import logging
from json import JSONDecodeError
from typing import Any, Dict, Optional

import httpx

from openderisk_cli import __version__
from openderisk_cli.config import OpenDeriskConfig
from openderisk_cli.exceptions import APIError

logger = logging.getLogger(__name__)


class OpenDeriskHttpClient:
    """Base HTTP client for OpenDerisk API.

    Note: OpenDerisk does not require authentication.
    """

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        config: Optional[OpenDeriskConfig] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.config = config
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": f"openderisk-cli/{__version__}",
            }

            self._client = httpx.Client(
                base_url=self.base_url, timeout=self.timeout, headers=headers, verify=False
            )
        return self._client

    def _make_request(
        self,
        method: str,
        path: str,
        json: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make HTTP request.

        Args:
            method: HTTP method
            path: API path
            json: JSON body
            params: Query parameters
            headers: Additional headers
            **kwargs: Additional arguments for httpx

        Returns:
            JSON response

        Raises:
            APIError: If request fails
        """
        url = f"{self.base_url}{path}"
        request_headers = {"User-Agent": f"openderisk-cli/{__version__}"}
        if headers:
            request_headers.update(headers)

        try:
            logger.debug(f"Request: {method} {url}")
            logger.debug(f"Request params: {params}")
            logger.debug(f"Request json: {json}")
            response = self.client.request(
                method=method, url=url, json=json, params=params, headers=request_headers, **kwargs
            )
            response.raise_for_status()
            try:
                resp = response.json() if response.content else {}
            except JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {response.text[:500]}")
                raise APIError(
                    message="Server returned invalid JSON response",
                    details=f"Response content: {response.text[:200] if response.text else 'empty'}",
                    suggestion="Please check if the server is running properly",
                )
            logger.debug(f"Response body: {resp}")
            return resp
        except httpx.HTTPStatusError as e:
            raise APIError(
                message=f"API request failed: {e.response.status_code}",
                status_code=e.response.status_code,
                response=self._safe_parse_json(e.response),
                details=str(e),
                suggestion="Check your request parameters and try again",
            )
        except httpx.RequestError as e:
            raise APIError(
                message="Network error",
                details=str(e),
                suggestion="Check your network connection and try again",
            )

    def _safe_parse_json(self, response: httpx.Response) -> Dict[str, Any]:
        """Safely parse JSON response."""
        try:
            return response.json()
        except Exception:
            return {"text": response.text}

    def get(self, path: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        return self._make_request("GET", path, params=params, **kwargs)

    def post(self, path: str, json: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        return self._make_request("POST", path, json=json, **kwargs)

    def put(self, path: str, json: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make PUT request."""
        return self._make_request("PUT", path, json=json, **kwargs)

    def delete(self, path: str, **kwargs) -> Dict[str, Any]:
        """Make DELETE request."""
        return self._make_request("DELETE", path, **kwargs)

    def stream(
        self,
        method: str,
        path: str,
        json: Optional[Dict] = None,
        **kwargs,
    ):
        """Make streaming request.

        Args:
            method: HTTP method
            path: API path
            json: JSON body
            **kwargs: Additional arguments for httpx

        Yields:
            Stream lines
        """
        url = f"{self.base_url}{path}"
        with self.client.stream(method, url, json=json, **kwargs) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                yield line

    def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
