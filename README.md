# Order Book Aggregator 

simple script to pull BTC USD pair order books from coinbase pro and gemini to find simulated execution price.

## Setup instructions : 

i have included 2 options to get the script up and running - 

**Option 1 : use pyenv :**

```python
python -m venv venv
source venv/bin/activate #or platform equivalent command

pip install -r requirements.txt

python order_router.py --qty <qty here> 
```

**Option 2 : use docker :**

```python
docker build -t orderbook .
docker run orderbook --qty <qty here>
```

## Assumptions : 

- Simulation of exchange rate limiting refers to 429 error code being raised due to consecutive calls (within a 2 second interval)
- We rely on only simulated rate limiting errors , no handling for actual exchange errors in current script
- We assume liquidity is present on both exchanges , insufficient liquidity conditions aren't handled.
- We assume market order execution , not limit order execution.
- We assume no transaction / maker / taker fees or slippage handling is required 
- We assume no efficient sorting algorithms required for walking the order book.
- We assume response payloads and payload fields for both the endpoints work according to the preliminary analysis done (attached notebook for prelim analysis as well)
- We assume no other output details required other than total cost of acquiring x amount of BTC
- We assume cases for target amount not being reached don't need handling
