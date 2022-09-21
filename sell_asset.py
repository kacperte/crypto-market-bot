import redis
from okex_bot import OkexBot
from dotenv import load_dotenv
from os import getenv
from db import SessionLocal, add_to_transaction_db
import time

load_dotenv()

# OKEX API credentials
APIKEY = getenv("APIKEY")
APISECRET = getenv("APISECRET")
PASS = getenv("PASS")
BASEURL = getenv("BASEURL")

# init Session
session = SessionLocal()


class SellAsset(OkexBot):

    def __init__(self, coin_id: str, APIKEY, APISECRET, PASS, BASEURL):
        super().__init__(APIKEY, APISECRET, PASS, BASEURL)
        self.client = redis.Redis(host='localhost', port=6379)

    def sell_position(self, coin_id, percentage_of_sales):
        balnce = self.get_balance(coin_id)
        volumen_to_sell = balnce * percentage_of_sales
        order = self.place_market_order(pair=coin_id, side='sell', amount=volumen_to_sell)
        # wait 1 s for the transaction details to be created
        time.sleep(1)
        # set order information
        order_infofation = self.get_info_about_last_orders()[0]
        add_to_transaction_db(
            session,
            instId=order_infofation["instId"],
            side=order_infofation["side"],
            ordId=order_infofation["ordId"]
        )
        if percentage_of_sales < 1:
            parms = [2, 0.8, 0.5, 1]
            parms = " ".join([str(i) for i in parms])
            self.client.publish('new_position', parms)


if __name__ == "__main__":
    # use loop to listen new message
    while True:
        redis = redis.Redis(host='localhost', port=6379)
        sub = redis.pubsub()
        sub.subscribe('sell_asset')
        for message in sub.listen():
            if message['type'] == 'message':
                parms = str(message.get('data')).split("'")[1].split(" ")
                SellAsset(
                    APISECRET=APISECRET,
                    APIKEY=APIKEY,
                    PASS=PASS,
                    BASEURL=BASEURL
                ).sell_position(
                    coin_id=parms[0],
                    percentage_of_sales=float(parms[1]),
                )

