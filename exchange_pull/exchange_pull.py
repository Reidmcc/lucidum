import ccxt
import psycopg2 # all sql is for postgres, adapt for your implementation if different
import time

# connect to your database
conn = psycopg2.connect("dbname=lucidum user=postgres password=postgres")

# use whichever exchange you prefer, though ccxt call coverage varies
ex_string = "binance"
ex = ccxt.binance() 

# check markets as necessary
# print(ex.load_markets())

# make a list of the markets you want to track
markets = ["XLM/BTC", "ETH/BTC", "XRP/BTC", "EOS/BTC", "LTC/BTC", "BCH/BTC", "BNB/BTC"]
        
# get the candles to populate the running ohlcv table
# choose your intervals; check your exchange's API reference for valid options
# historical day-level data is findable online; it's the shorter invervals we're after
intervals = ["1m","5m", "30m", "1h", "4h"]

# candles all go in one table with a composite key: (exchange, market, c_timestamp, c_interval)
# if your exchange doesn't use UNIX timestamps, convert them
cur = conn.cursor()

while True:
    for m in markets:
        print("Market=",m)
        for i in intervals: 
            print("interval=",i)
            candles = ex.fetch_ohlcv(m, i)
            for c in candles:
                # you need to make sure you're not inseting duplicates
                # in postgres ON CONFLICT DO NOTHING takes care of this
                cur.execute("INSERT INTO CANDLES (exchange, market, c_timestamp, c_interval, c_open, c_high, c_low, c_close, c_volume) \
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;""",
                    (ex_string, m, int(c[0]), i, float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5])))
        time.sleep(int(1)) #you may be making a lot of API calls, so rest a bit


    cur.execute("SELECT * FROM CANDLES;")
    a = cur.fetchall()
    conn.commit()
    print(len(a)) # Look on my table, ye Mighty, and despair

    # wait for the shortest interval you're measuring
    time.sleep(int(60))