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
                    print(f'[Rate Limited] sleeping for : {sleep_interval} , attempt : {attempts} of {max_retries}')
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
    parsed_bids.sort(key= lambda x: x[0], reverse=True)
    parsed_asks.sort(key= lambda x: x[0])
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
    parsed_bids.sort(key= lambda x: x[0], reverse=True)
    parsed_asks.sort(key= lambda x: x[0])
    return parsed_bids, parsed_asks


for i in range(5):
    print(get_gemini_ob())
print(get_coinbase_ob())
