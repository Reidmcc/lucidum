import ccxt
import psycopg2 # all sql is for postgres, adapt for your implementation if different
import time
from datetime import datetime
from datetime import timedelta
import traceback
import random

class exchange:
    def __init__(self, name, api, intervals, markets=None, lookback=500):
        self.name = name
        self.api = api
        self.intervals = intervals
        if markets != None:
            self.specified_markets = True
            self.markets = markets
        else:
            self.specified_markets = False
            self.markets = None
        self.lookback = lookback
        self.ratelimit = self.api.describe()['rateLimit']

    def wait(self, n=1):
        time.sleep(self.ratelimit / 1000 * n)

    def get_markets(self):
        if self.specified_markets:
            return self.markets
        else:
            markets = self.api.load_markets()
            return markets.keys()

# if you want specific markets, assign them to 'markets=' when defining exchanges, e.g.
    # markets = ["XLM/BTC", "ETH/BTC", "XRP/BTC", "EOS/BTC", "LTC/BTC", "BCH/BTC", "BNB/BTC"]
# otherwise deploy firehose mode and pull every market
# check your exchange's API reference  for valid interval options (if their API gives them in seconds convert to ccxt Xm/Xh/Xd format)
# ccxt has rate-limits in the exchange classes, but they may vary by API endpoint
# some exchanges throttle OHLCV calls by data point, use 'lookback=', specified in number of candles, to limit your pulls

# use whichever exchange you prefer, though ccxt call coverage varies
coinbasepro = exchange('coinbasepro', ccxt.coinbasepro(), ['1m', '5m', '15m', '1h', '6h'], lookback=100)
binance = exchange('binance', ccxt.binance(), ["1m","5m", "30m", "1h", "4h"])

exchanges = (coinbasepro, binance)
      
# candles all go in one table with a composite key: (exchange, market, c_timestamp, c_interval)
# if your exchange doesn't use UNIX timestamps, convert them

while True:
    conn = psycopg2.connect("dbname=lucidum user=postgres password=postgres")
    cur = conn.cursor()
    for ex in exchanges:
        try:
            print('Pulling from {}'.format(ex.name))
            markets = ex.get_markets()
            for m in markets:
                print("Market=",m)
                for i in ex.intervals: 
                    print("interval=",i)
                    candles = ex.api.fetch_ohlcv(m, i, limit=ex.lookback)
                    for c in candles:
                        # you need to make sure you're not inserting duplicates
                        # in postgres ON CONFLICT DO NOTHING takes care of this
                        cur.execute("INSERT INTO CANDLES (exchange, market, c_timestamp, c_interval, c_open, c_high, c_low, c_close, c_volume) \
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;""",
                            (ex.name, m, int(c[0]), i, float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5])))
                    if ex.name == 'coinbasepro':
                        ex.wait(3) 
                    else:
                        ex.wait() #you may be making a lot of API calls, so wait between interval calls
                conn.commit()
        except:
            traceback.print_exc()
    
    cur.execute("SELECT count(*) FROM CANDLES;")
    a = cur.fetchall()    
    print(len(a)) # Look on my table, ye Mighty, and despair
    cur.close()
    conn.close()
    del(cur, conn, a) # if you're not careful you'll end of with a lot of huge cursor, connection, and 'a' objects in memory

    print("queried all markets")
    # wait for more data to exist
    print("waiting...")
    time.sleep(300)