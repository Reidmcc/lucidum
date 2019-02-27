--this is the code to create your database tables in Postgres; should be similar for other SQL implementations
create table candles (
    exchange varchar(50) null
    , market varchar(10) null
    , c_timestamp bigint null  --this should be converted to UNIX time whatever the source is
    , c_interval varchar(50) null
    , c_open float null 
    , c_high float null
    , c_low float null
    , c_close float null
    , c_volume float null
    primary key (exchange, market, c_timestamp, c_interval) --that's one hell of a composite key!
)


