import requests
import redis
from db import SessionLocal, add_to_new_token_db

# init Redis
redis = redis.Redis(host='localhost', port=6379)

# OKX API URL
url = "https://www.okx.com/priapi/v5/rubik/app/public/new-coin-rank?t=1661446882241&type=USDT"

# init Session
session = SessionLocal()


def stream():
    """Function to listen for OKEX API and to catch new tokens"""
    # actual list of tokens on OKEX
    list_of_coins = requests.get(url).json()['data'][0]['online']
    # number of tokens on OKEX
    len_list_of_coins = len(list_of_coins)
    while True:
        # condition that check if there is new token
        if len(requests.get(url).json()['data'][0]['online']) > len_list_of_coins:
            # set new token ID
            new_coin = [x for x in requests.get(url).json()['data'][0]['online'] if x not in list_of_coins][0]["instId"]
            # publish to redis information about new token
            redis.publish('token_id', new_coin)
            # post to db inforamtion
            add_to_new_token_db(session, instId=new_coin, market='okex')
            # update the following variables with new data
            list_of_coins = requests.get(url).json()['data'][0]['online']
            len_list_of_coins = len(requests.get(url).json()['data'][0]['online'])

        print("Checking for new coin...")
