import json
import re
import logging
import os
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from dotenv import load_dotenv
import aiohttp
import websockets

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "https://dwapi.dawonai.com:18443/iot2"
WS_TIMEOUT = int(os.getenv("WS_TIMEOUT", "2"))
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "2"))

DEFAULT_HEADERS = {
    "user-agent": f"Mozilla/5.0 (Linux; Android 15; {os.getenv('TERMINAL_NAME', 'Generic')} Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/139.0.7258.94 Mobile Safari/537.36",
    "accept": "*/*",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Android WebView";v="139", "Chromium";v="139"',
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "sec-ch-ua-mobile": "?1",
    "origin": "https://dwapi.dawonai.com:18443",
    "sec-fetch-site": "same-origin",
    "referer": "https://dwapi.dawonai.com:18443/iot2/login/login.opi?lang=ko",
    "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}


class DwClientError(Exception):
    pass


class AuthenticationError(DwClientError):
    pass


class SessionError(DwClientError):
    pass


class NetworkError(DwClientError):
    pass


@dataclass
class WebSocketPayload:
    ws_uri: str
    message: str


class DwClient:
    def __init__(self):
        self.cookie_jar = aiohttp.CookieJar()
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = BASE_URL
        self._login_attempts: int = 0
        self._max_login_attempts: int = 3

    def _validate_environment(self) -> None:
        required_vars = ["USER_ID", "SSO_TOKEN", "TERMINAL_ID", "TERMINAL_NAME"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise AuthenticationError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        logger.info("Environment variables validated")

    async def __aenter__(self):
        try:
            self.session = aiohttp.ClientSession(
                cookie_jar=self.cookie_jar,
                headers=DEFAULT_HEADERS,
                timeout=aiohttp.ClientTimeout(total=30),
            )
            logger.info("Client session initialized")
            return self
        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            raise SessionError(f"Session initialization failed: {e}")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session and not self.session.closed:
            try:
                await self.session.close()
                logger.info("Client session closed")
            except Exception as e:
                logger.error(f"Error closing session: {e}")

    async def login(self) -> bool:
        if self.session is None:
            raise RuntimeError("Session not initialized")

        try:
            self._validate_environment()
        except AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            return False

        self._login_attempts += 1
        if self._login_attempts > self._max_login_attempts:
            logger.error("Max login attempts exceeded")
            return False

        try:
            async with self.session.post(
                f"{self.base_url}/member/loginAction.opi",
                data={
                    "user_id": os.getenv("USER_ID"),
                    "sso_token": os.getenv("SSO_TOKEN"),
                    "terminal_id": os.getenv("TERMINAL_ID"),
                    "terminal_name": os.getenv("TERMINAL_NAME"),
                },
            ) as response:
                if response.status == 200:
                    self._login_attempts = 0
                    logger.info("Login successful")
                    return True
                else:
                    logger.error(f"Login failed with status: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    async def _is_session_expired(self, response_text: str) -> bool:
        return (
            '<meta http-equiv="refresh"' in response_text
            and "/iot2/login/" in response_text
        ) or "login" in response_text.lower()

    async def _request_with_retry(self, request_func, *args, **kwargs) -> Optional[Any]:
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                response_data = await request_func(*args, **kwargs)

                if response_data is None and attempt < MAX_RETRY_ATTEMPTS - 1:
                    logger.warning("Session expired, attempting re-login...")
                    if await self.login():
                        logger.info("Re-login successful, retrying request...")
                        continue
                    else:
                        logger.error("Re-login failed")
                        return None

                return response_data

            except Exception as e:
                logger.error(f"Request error on attempt {attempt + 1}: {e}")
                if attempt < MAX_RETRY_ATTEMPTS - 1:
                    continue
                raise

        return None

    async def get_devices(self) -> Optional[List[Dict[str, Any]]]:
        async def _get_devices_internal() -> Optional[List[Dict[str, Any]]]:
            if self.session is None:
                raise RuntimeError("Session not initialized")

            try:
                async with self.session.get(
                    f"{self.base_url}/product/device_list.opi"
                ) as response:
                    if response.status == 200:
                        text = await response.text()

                        if await self._is_session_expired(text):
                            logger.warning("Session expired in get_devices")
                            return None

                        try:
                            return json.loads(text).get("devices", [])
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse devices JSON: {e}")
                            return None
                    else:
                        logger.error(f"Failed to get devices: {response.status}")
                        return None
            except Exception as e:
                logger.error(f"Error in get_devices: {e}")
                raise NetworkError(f"Network error: {e}")

        return await self._request_with_retry(_get_devices_internal)

    async def get_websocket_payload(self, device_id: str) -> Optional[WebSocketPayload]:
        async def _get_websocket_payload_internal() -> Optional[WebSocketPayload]:
            if self.session is None:
                raise RuntimeError("Session not initialized")

            try:
                async with self.session.get(
                    f"{self.base_url}/product/productDetailPlug.opi?deviceId={device_id}"
                ) as response:
                    if response.status == 200:
                        html_content = await response.text()

                        if await self._is_session_expired(html_content):
                            logger.warning("Session expired in get_websocket_payload")
                            return None

                        ws_uri_match = re.search(
                            r'var\s+wsUri\s*=\s*["\']([^"\']+)["\']', html_content
                        )
                        ws_uri = ws_uri_match.group(1) if ws_uri_match else None

                        message_match = re.search(
                            r'var\s+message\s*=\s*["\']([^"\']*)["\']', html_content
                        )
                        message = message_match.group(1) if message_match else None

                        if not ws_uri or not message:
                            logger.error(
                                f"Failed to extract WebSocket payload for device {device_id}"
                            )
                            return None

                        return WebSocketPayload(ws_uri=ws_uri, message=message)
                    else:
                        logger.error(f"Failed to get websocket data: {response.status}")
                        return None
            except Exception as e:
                logger.error(f"Error in get_websocket_payload: {e}")
                raise NetworkError(f"Network error: {e}")

        result = await self._request_with_retry(_get_websocket_payload_internal)
        if isinstance(result, dict):
            return WebSocketPayload(
                ws_uri=result.get("wsUri", ""), message=result.get("message", "")
            )
        return result

    async def get_websocket_data(
        self, ws_uri: str, message: str
    ) -> Optional[List[str]]:
        try:
            logger.debug(f"Connecting to WebSocket: {ws_uri}")

            cookie_header = None
            if self.session and self.session.cookie_jar:
                cookies = []
                for cookie in self.session.cookie_jar:
                    cookies.append(f"{cookie.key}={cookie.value}")
                if cookies:
                    cookie_header = "; ".join(cookies)

            headers = {}
            if cookie_header:
                headers["Cookie"] = cookie_header
            headers["User-Agent"] = DEFAULT_HEADERS["user-agent"]
            headers["Origin"] = DEFAULT_HEADERS["origin"]

            responses: List[str] = []
            async with websockets.connect(
                ws_uri, additional_headers=headers
            ) as websocket:
                logger.debug("WebSocket connected successfully")

                logger.debug(f"Sending message: {message}")
                await websocket.send(message)

                try:
                    for i in range(3):
                        response = await asyncio.wait_for(
                            websocket.recv(), timeout=WS_TIMEOUT
                        )
                        if isinstance(response, (bytes, bytearray)):
                            response = response.decode("utf-8")
                        elif isinstance(response, memoryview):
                            response = response.tobytes().decode("utf-8")
                        logger.debug(
                            f"Received WebSocket message {i + 1}: {response[:100]}..."
                        )
                        responses.append(response)
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout after receiving {len(responses)} messages")
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("WebSocket connection closed by server")

            return responses

        except websockets.exceptions.WebSocketException as e:
            logger.error(f"WebSocket connection failed: {e}")
            raise NetworkError(f"WebSocket error: {e}")
        except Exception as e:
            logger.error(f"Unexpected WebSocket error: {e}")
            raise NetworkError(f"Unexpected error: {e}")

    async def get_current_data(self, device_id: str) -> Optional[Dict[str, Any]]:
        websocket_payload = await self.get_websocket_payload(device_id)

        if (
            not websocket_payload
            or not websocket_payload.ws_uri
            or not websocket_payload.message
        ):
            logger.error(f"Failed to get websocket payload for device {device_id}")
            return None

        try:
            responses = await self.get_websocket_data(
                websocket_payload.ws_uri, f"{websocket_payload.message};{device_id}"
            )

            if not responses:
                logger.error(f"No websocket responses for device {device_id}")
                return None

            key_mapping = {
                "value_power": "powered",
                "value_watt": "current_watt",
                "value_watth": "monthly_kwh",
                "value_product_temp": "temperature",
            }

            combined_data: Dict[str, Any] = {}
            for response in responses:
                if not isinstance(response, str):
                    logger.warning(f"Skipping non-string response: {type(response)}")
                    continue

                try:
                    data: Dict[str, Any] = json.loads(response)
                    for key, value in data.items():
                        if key not in ["device_id", "conn_status"]:
                            mapped_key: str = key_mapping.get(key, key)

                            if mapped_key == "powered":
                                combined_data[mapped_key] = str(value).lower() in (
                                    "true",
                                    "1",
                                    "on",
                                    "yes",
                                )
                            elif mapped_key in [
                                "current_watt",
                                "monthly_kwh",
                                "temperature",
                            ]:
                                try:
                                    combined_data[mapped_key] = float(value)
                                except (ValueError, TypeError):
                                    logger.warning(
                                        f"Failed to convert {mapped_key} to float: {value}"
                                    )
                                    combined_data[mapped_key] = None
                            else:
                                combined_data[mapped_key] = value

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse WebSocket response: {e}")
                    continue

            return combined_data

        except NetworkError:
            raise
        except Exception as e:
            logger.error(f"Error in get_current_data: {e}")
            raise DwClientError(f"Failed to get current data: {e}")

    async def get_chart_data(
        self, device_id: str, target: str, metric: str
    ) -> Optional[Dict[str, Any]]:
        async def _get_chart_data_internal() -> Optional[Dict[str, Any]]:
            if self.session is None:
                raise RuntimeError("Session not initialized")

            try:
                async with self.session.post(
                    f"{self.base_url}/product/get_chart_data.opi",
                    data={
                        "device_id": device_id,
                        "resource_uri": "/100/0/21",
                        "target": target,
                        "type": "avg",
                        "showdiv": metric.upper(),
                    },
                ) as response:
                    if response.status == 200:
                        text = await response.text()

                        if await self._is_session_expired(text):
                            logger.warning("Session expired in get_chart_data")
                            return None

                        try:
                            r = json.loads(text)
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON decode error: {e}")
                            return None

                        chart_data = r.get("statistic", {}).get("stat_info", [])
                        chart_data_old = r.get("statistic", {}).get("stat_info_old", [])

                        key_mapping = {"n": "date", "sv": "value", "unit": "unit"}

                        def transform_chart_item(
                            item: Dict[str, Any],
                        ) -> Dict[str, Any]:
                            transformed = {
                                key_mapping.get(key, key): value
                                for key, value in item.items()
                            }
                            return transformed

                        return {
                            "data": [transform_chart_item(item) for item in chart_data],
                            "old_data": [
                                transform_chart_item(item) for item in chart_data_old
                            ],
                        }
                    else:
                        logger.error(f"Failed to get chart data: {response.status}")
                        return None
            except Exception as e:
                logger.error(f"Error in get_chart_data: {e}")
                raise NetworkError(f"Network error: {e}")

        return await self._request_with_retry(_get_chart_data_internal)
