import redis
from okex_bot import OkexBot
from dotenv import load_dotenv
from os import getenv
from db import SessionLocal, add_to_sales_alert_db

load_dotenv()

# OKEX API credentials
APIKEY = getenv("APIKEY")
APISECRET = getenv("APISECRET")
PASS = getenv("PASS")

# init Session
session = SessionLocal()


class PriceChecker(OkexBot):
    """The class inherits from OKEX Bot. If the price reaches the expected level, it triggers the sale"""
    def __init__(self, APIKEY, APISECRET, PASS):
        super().__init__(APIKEY, APISECRET, PASS)
        self.client = redis.Redis(host='localhost', port=6379)
        self.order_info = self.get_info_about_last_orders()[0]
        self.usdt_balance = self.get_balance('USDT')
        self.purchase_price = float(self.order_info['fillPx'])

    def price_tracking(self, profit, losses, volumen_profit, volumen_losses):
        while True:
            # set current price of token
            current_price = float(self.check_price(self.order_info['instId']))
            # condition to sell for profit
            if current_price >= self.purchase_price * profit:
                # publish to redis information to place new order - sell (token_id/volumen_profit)
                parms = [self.order_info['instId'],  volumen_profit]
                parms = " ".join([str(i) for i in parms])
                self.client.publish('sell_asset', parms)
                # post to db inforamtion
                add_to_sales_alert_db(
                    session,
                    type='profit',
                    volumenOfSale=volumen_profit,
                    percent=profit,
                    price=current_price,
                    instId=self.order_info['instId'],
                )
            # condition to sell for losses
            elif current_price <= self.purchase_price * losses:
                # publish to redis information to place new order - sell (token_id/volumen_profit)
                parms = [self.order_info['instId'], volumen_losses]
                parms = " ".join([str(i) for i in parms])
                self.client.publish('sell_asset', parms)
                # post to db inforamtion
                add_to_sales_alert_db(
                    session,
                    type='losses',
                    volumenOfSale=volumen_losses,
                    percent=losses,
                    price=current_price,
                    instId=self.order_info['instId'],
                )


if __name__ == "__main__":
    # use loop to listen new message
    while True:
        redis = redis.Redis(host='localhost', port=6379)
        sub = redis.pubsub()
        sub.subscribe('new_position')
        for message in sub.listen():
            if message['type'] == 'message':
                parms = str(message.get('data')).split("'")[1].split(" ")
                PriceChecker(
                    APISECRET=APISECRET,
                    APIKEY=APIKEY,
                    PASS=PASS
                ).price_tracking(
                    profit=float(parms[0]),
                    losses=float(parms[1]),
                    volumen_profit=float(parms[2]),
                    volumen_losses=float(parms[3])
                )