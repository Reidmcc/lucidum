*You know that feeling where you want an absurd amount of cryptocurrency market data? Yeah, me too.*

**Lucidum** is a data scraper and database for cryptocurrency exchange API data. For now it's just the `candles` table definition and the `exchange_pull` python script for scraping OHLCV data via ccxt. It will get you tens of thousands of data points with just those.

To use lucidum:

1. Install [PostgreSQL](https://www.postgresql.org/). Or any SQL database, really. The code as written is for Postgres
2. Create a database: `lucidum`
3. Using the code from *build_db/tables.sql*, create your `candles` table
4. Set your user and password at the top of the Python script
5. Run the script

Enjoy!
