import json
import requests
import time
from functools import wraps

RATE_LIMIT_DICT = {}

class RateLimitError(Exception):
    pass

def rate_limit_handler(max_retries = 6, sleep_time = 2, backoff = 2):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            sleep_interval = sleep_time
            attempts = 0
            while True:
                try:
                    return function(*args, **kwargs)
                except RateLimitError:
                    attempts += 1
                    if attempts > max_retries:
                        raise
                    print(f'[Rate Limited] sleeping for : {sleep_interval} s , attempt : {attempts} of {max_retries}')
                    time.sleep(sleep_interval)
                    sleep_interval = sleep_interval * backoff
        return wrapper
    return decorator


def request_simulator(url : str) -> requests.Response:
    ''' 
    Simulates Exchange Rate limiting 
    '''
    last_call_ts = RATE_LIMIT_DICT.get(url)
    curr_time = time.time()
    if last_call_ts and ((curr_time - last_call_ts) < 2):
        resp = requests.Response()
        resp.status_code = 429 # assuming too many requests code from exchange
        return resp
    RATE_LIMIT_DICT[url] = curr_time

    resp = requests.get(url)
    return resp

def get(url : str) -> requests.Response:
    resp = request_simulator(url)

    if resp.status_code == 200:
        return resp
    elif resp.status_code == 429: 
        raise RateLimitError("too many requests")
    else:
        raise Exception("unexpected status code received")

@rate_limit_handler(max_retries=3, sleep_time=2, backoff=2)
def get_gemini_ob():
    url = 'https://api.gemini.com/v1/book/BTCUSD'
    resp = get(url)
    resp_payload = json.loads(resp.text)
    bids = resp_payload.get('bids')
    asks = resp_payload.get('asks')
    parsed_bids = [[float(bid.get('price')), float(bid.get('amount'))] for bid in bids]
    parsed_asks = [[float(ask.get('price')), float(ask.get('amount'))] for ask in asks]
    return parsed_bids, parsed_asks

@rate_limit_handler(max_retries=3, sleep_time=2, backoff=2)
def get_coinbase_ob():
    url = 'https://api.exchange.coinbase.com/products/BTC-USD/book?level=2'
    resp = get(url)
    resp_payload = json.loads(resp.text)
    bids = resp_payload.get('bids')
    asks = resp_payload.get('asks')
    parsed_bids = [[float(bid[0]), float(bid[1])] for bid in bids]
    parsed_asks = [[float(ask[0]), float(ask[1])] for ask in asks]
    return parsed_bids, parsed_asks

def walk_book(total_amount, bids, asks, side='buy'):

    amount_filled=0.0
    total_cost = 0.0
    if side == 'buy':
        book = bids
    else:
        book = asks

    for price, quantity in book:

        transaction = min(quantity, total_amount - amount_filled)
        amount_filled += transaction
        print(f'[{side}ing] {transaction} / {total_amount} at {price}')
        total_cost += price * transaction
        
        if amount_filled == total_amount:
            break
    
    average_price = total_cost / amount_filled
    return amount_filled, average_price

gemini_bids, gemini_asks = get_gemini_ob()
cb_bids, cb_asks = get_coinbase_ob()

agg_bids = gemini_bids + cb_bids
agg_asks = gemini_asks + cb_asks
agg_bids.sort(key= lambda x : x[0], reverse=True)
agg_asks.sort(key= lambda x : x[0])

btc_amount = 100
btc_bought , btc_bought_price = walk_book(btc_amount, agg_bids, agg_asks, side='buy')
btc_sold , btc_sold_price = walk_book(btc_amount, agg_bids, agg_asks, side='sell')

print(btc_bought, btc_bought_price)
print(btc_sold , btc_sold_price )