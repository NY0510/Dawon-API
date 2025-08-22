import json
import re
from dotenv import load_dotenv
import aiohttp
import os
import asyncio
import websockets

load_dotenv()

BASE_URL = 'https://dwapi.dawonai.com:18443/iot2'

DEFAULT_HEADERS = {
    'user-agent': f"Mozilla/5.0 (Linux; Android 15; {os.getenv('TERMINAL_NAME')} Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/139.0.7258.94 Mobile Safari/537.36",
    'accept': '*/*',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Android WebView";v="139", "Chromium";v="139"',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'sec-ch-ua-mobile': '?1',
    'origin': 'https://dwapi.dawonai.com:18443',
    'sec-fetch-site': 'same-origin',
    'referer': 'https://dwapi.dawonai.com:18443/iot2/login/login.opi?lang=ko',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
}

class DwClient:
    def __init__(self):
        self.cookie_jar = aiohttp.CookieJar()
        self.session = None
        self.base_url = BASE_URL
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            cookie_jar=self.cookie_jar,
            headers=DEFAULT_HEADERS
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def login(self):
        async with self.session.post(f'{self.base_url}/member/loginAction.opi',
            data={
                'user_id': os.getenv('USER_ID'),
                'sso_token': os.getenv('SSO_TOKEN'),
                'terminal_id': os.getenv('TERMINAL_ID'),
                'terminal_name': os.getenv('TERMINAL_NAME'),
            }
        ) as response:
            if response.status == 200:
                print("Login successful")
                return True
            else:
                print(f"Login failed with status: {response.status}")
                return False
                
    async def get_devices(self):
        async with self.session.get(f'{self.base_url}/product/device_list.opi') as response:
            if response.status == 200:
                text = await response.text()
                return json.loads(text).get('devices', [])
            else:
                print(f"Failed to get devices: {response.status}")
                return None
            
    async def get_websocket_payload(self, device_id: str):
        async with self.session.get(f'{self.base_url}/product/productDetailPlug.opi?deviceId={device_id}') as response:
            if response.status == 200:
                html_content = await response.text()
                
                # wsUri 추출
                ws_uri_match = re.search(r'var\s+wsUri\s*=\s*["\']([^"\']+)["\']', html_content)
                ws_uri = ws_uri_match.group(1) if ws_uri_match else None
                
                # message 추출 
                message_match = re.search(r'var\s+message\s*=\s*["\']([^"\']*)["\']', html_content)
                message = message_match.group(1) if message_match else None
                
                return {
                    'wsUri': ws_uri,
                    'message': message,
                }
            else:
                print(f"Failed to get websocket data: {response.status}")
                return None
    
    async def get_websocket_data(self, ws_uri: str, message: str):
        try:
            print(f"Connecting to WebSocket: {ws_uri}")
            
            # 쿠키를 헤더로 변환
            cookie_header = None
            if self.session and self.session.cookie_jar:
                cookies = []
                for cookie in self.session.cookie_jar:
                    cookies.append(f"{cookie.key}={cookie.value}")
                if cookies:
                    cookie_header = "; ".join(cookies)
            
            # 웹소켓 연결용 헤더 설정
            headers = {}
            if cookie_header:
                headers['Cookie'] = cookie_header
            headers['User-Agent'] = DEFAULT_HEADERS['user-agent']
            headers['Origin'] = DEFAULT_HEADERS['origin']
            
            async with websockets.connect(ws_uri, additional_headers=headers) as websocket:
                print("WebSocket connected successfully")
                
                # 메시지 전송
                print(f"Sending message: {message}")
                await websocket.send(message)
                
                # 메시지 3개만 수신
                responses = []
                try:
                    for i in range(3):
                        response = await asyncio.wait_for(websocket.recv(), timeout=2)
                        responses.append(response)
                        
                except asyncio.TimeoutError:
                    print("No more messages received within timeout")
                except websockets.exceptions.ConnectionClosed:
                    print("WebSocket connection closed by server")
                    
                return responses
                
        except websockets.exceptions.WebSocketException as e:
            print(f"WebSocket connection failed: {e}")
            return None
        except Exception as e:
            print(f"WebSocket connection error: {e}")
            return None
        
    async def get_chart_data(self, device_id: str, target: str, metric: str):
        async with self.session.post(f'{self.base_url}/product/get_chart_data.opi',
            data={
                'device_id': device_id,
                'resource_uri': '/100/0/21',
                'target': target,
                'type':'avg',
                'showdiv': metric.upper(),
            }
        ) as response:
            if response.status == 200:
                text = await response.text()
                return json.loads(text)
            else:
                print(f"Failed to get chart data: {response.status}")
                return None
            
    async def get_current_data(self, device_id: str):
        websocket_data = await self.get_websocket_payload(device_id)
        ws_uri = websocket_data.get('wsUri')
        message = websocket_data.get('message')
        
        if not websocket_data or not ws_uri or not message:
            print("Failed to get websocket data")
            return None
            
        # 웹소켓 메시지 수신
        responses = await self.get_websocket_data(ws_uri, f'{message};{device_id}')
        if not responses:
            print("Failed to get websocket responses")
            return None
            
        key_mapping = {
            'value_power': 'powered',
            'value_watt': 'current_watt', 
            'value_watth': 'monthly_kwh',
            'value_product_temp': 'temperature'
        }
        
        combined_data = {}
        for response in responses:
            try:
                data = json.loads(response)
                for key, value in data.items():
                    if key not in ['device_id', 'conn_status']:
                        mapped_key = key_mapping.get(key, key)
                        combined_data[mapped_key] = value
                        
            except json.JSONDecodeError as e:
                print(f"Failed to parse response: {response}, error: {e}")
                continue
                
        return combined_data
        