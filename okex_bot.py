import base64
import datetime as dt
import hmac
import requests
import json
from decimal import Decimal


class OkexBot:
    """A bot to perform operations on OKEX"""
    def __init__(self, APIKEY: str, APISECRET: str, PASS: str, baseURL: str):
        self.apikey = APIKEY
        self.apisecret = APISECRET
        self.password = PASS
        self.baseurl = baseURL

    # get a current price of token
    @staticmethod
    def check_price(id: str):
        return requests.get(f'https://okex.com/api/v5/market/ticker?instId={id}').json()['data'][0]['last']

    # get the time according to the API
    @staticmethod
    def get_time():
        return dt.datetime.utcnow().isoformat()[:-3] + 'Z'

    # preparing signature to verified in API
    @staticmethod
    def signature(timestamp, method, request_path, body, secret_key):
        message = timestamp + method + request_path + body
        return base64.b64encode(hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256').digest())

    # prepare header to verified in API
    def get_header(self, request='GET', endpoint='', body=''):
        cur_time = self.get_time()
        return {
            'CONTENT-TYPE': "application/json",
            'OK-ACCESS-KEY': self.apikey,
            'OK-ACCESS-SIGN': self.signature(cur_time, request, endpoint, body, self.apisecret),
            'OK-ACCESS-TIMESTAMP': cur_time,
            'OK-ACCESS-PASSPHRASE': self.password,
        }

    # get actual balance of token
    def get_balance(self, currency: str):
        url = self.baseURL + "/api/v5/account/balance"
        header = self.get_header("GET", "/api/v5/account/balance")
        response = requests.get(url, headers=header).json()['data'][0]['details']
        for obj in response:
            if obj['ccy'] != currency:
                continue

            return obj['availBal']

    # function to place market order buy/sell
    def place_market_order(self, pair, side, amount, tdMode='cash'):
        endpoint = '/api/v5/trade/order'
        url = self.baseURL + '/api/v5/trade/order'
        body = {
            "instId": pair,
            "tdMode": tdMode,
            "side": side,
            "ordType": "market",
            "sz": str(Decimal(str(amount)))
        }
        body = json.dumps(body)
        header = self.get_header("POST", endpoint, str(body))
        return requests.post(url, headers=header, data=body)

    # get transaction details (last 3 days）
    def get_info_about_last_orders(self, ):
        url = self.baseURL + "/api/v5/trade/fills"
        header = self.get_header("GET", "/api/v5/trade/fills")
        return requests.get(url, headers=header).json()["data"]

