import json
import requests

def get_gemini_ob():
    url = 'https://api.gemini.com/v1/book/BTCUSD'
    resp = requests.get(url)
    resp_payload = json.loads(resp.text)
    bids = resp_payload.get('bids')
    asks = resp_payload.get('asks')
    parsed_bids = [[float(bid.get('price')), float(bid.get('amount'))] for bid in bids]
    parsed_asks = [[float(ask.get('price')), float(ask.get('amount'))] for ask in asks]
    parsed_bids.sort(key= lambda x: x[0], reverse=True)
    parsed_asks.sort(key= lambda x: x[0])
    return parsed_bids, parsed_asks

def get_coinbase_ob():
    url = 'https://api.exchange.coinbase.com/products/BTC-USD/book?level=2'
    resp = requests.get(url)
    resp_payload = json.loads(resp.text)
    bids = resp_payload.get('bids')
    asks = resp_payload.get('asks')
    parsed_bids = [[float(bid[0]), float(bid[1])] for bid in bids]
    parsed_asks = [[float(ask[0]), float(ask[1])] for ask in asks]
    parsed_bids.sort(key= lambda x: x[0], reverse=True)
    parsed_asks.sort(key= lambda x: x[0])
    return parsed_bids, parsed_asks

print(get_gemini_ob())
print(get_coinbase_ob())
