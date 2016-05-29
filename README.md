# python-bitso #

A python wrapper for the [Bitso API](https://bitso.com/api_info/) 

[![Build Status](https://travis-ci.org/mariorz/python-bitso.svg?branch=master)](https://travis-ci.org/mariorz/python-bitso) [![Requirements Status](https://requires.io/github/mariorz/python-bitso/requirements.svg?branch=master)](https://requires.io/github/mariorz/python-bitso/requirements/?branch=master) 

# Public API Usage #

```python
 >>> import bitso
 >>> api = bitso.Api()
```


# Private API Usage #

```python
 >>> import bitso
 >>> api = bitso.Api(CLIENT_ID, API_KEY, API_SECRET)
```


# Public calls #

### Ticker ###

```python
## Ticker information
## Parameters
## [book = btc_mxn] - Specifies which book to use
##                  - string
 >>> tick = api.ticker()
 >>> tick
 Ticker(ask=7866.27, bid=7795.00, high=7866.27, last=7866.27, low=7707.43, datetime=2016-04-22 16:46:25, vwaplow=7795.00)
 >>> tick.last
 Decimal('7866.27')
 >>> tick.datetime
 datetime.datetime(2016, 4, 22, 16, 46, 53)
 ```


### Order Book ###

```python
## Public order book
## Parameters
## [book = btc_mxn] - Specifies which book to use
##                  - string
## [group = True] - Group orders with the same price
##                - boolean
>>> ob = api.order_book()
>>> ob.datetime  
datetime.datetime(2016, 4, 22, 18, 24, 58)
>>> ob.bids
[                  
  {
    'price': decimal,   ## Price for bid
    'amount': decimal   ## Amount bid
   }, ...
]

>>> ob.asks

[                   
  {
    'price': decimal,   ## Price for ask
    'amount': decimal   ## Amount asked
   }, ...
]

```

### Transactions ###

```python
## Public transactions
## Parameters
## [book = 'btc_mxn'] - Specifies which book to use
##                    - str
## [time = 'hour']    - Time frame for transaction export ('hour', 'minute')
##                    - str
>>> txs = api.transactions()
>>> txs
[Transaction(tid=91314, price=7864.10, amount=0.81446192, side=sell, datetime=2016-04-22 13:47:29),
 Transaction(tid=91313, price=7864.10, amount=0.32061901, side=sell, datetime=2016-04-22 13:36:18),
 Transaction(tid=91312, price=7863.72, amount=0.00357865, side=buy, datetime=2016-04-22 13:34:27),
 Transaction(tid=91311, price=7863.72, amount=0.74986010, side=sell, datetime=2016-04-22 13:34:07),
 ...
 ]

>>> txs[0].price
Decimal('7864.10')
>>> txs[0].amount
Decimal('0.81446192')
>>> txs[0].datetime 
datetime.datetime(2016, 4, 22, 13, 47, 29)

```


# Private calls #

Private endpoints are used to manage your account and your orders. These requests must be signed
with your [Bitso credentials](https://bitso.com/api_info#generating-api-keys) 

```python
 >>> import bitso
 >>> api = bitso.Api(CLIENT_ID, API_KEY, API_SECRET)
```

### Account Balance ###

```python
## Your account balance
>>> balance = api.balance()
>>> balance.mxn_balance
Decimal('4834.63')
>>> balance.btc_balance
Decimal('1.01300152')

```

### User Transactions ###

```python
## Your transactions
## Parameters
## [offset = 0]    - Skip that many transactions before beginning to return results
##                 - int
## [limit = 100]   - Limit result to that many transactions
##                 - int
## [sort = 'desc'] - Sorting by datetime
##                 - string - 'asc' or
##                 - 'desc'
## [book = btc_mxn]- Specifies which book to use
##                 - string
>>> utx = api.user_transactions()
>>> utx
[UserTransaction(type=trade, created_datetime=2016-04-21 23:17:39),
 UserTransaction(type=trade, created_datetime=2016-04-21 23:11:39),
 UserTransaction(type=trade, created_datetime=2016-04-21 21:40:07),
 UserTransaction(type=trade, created_datetime=2016-04-21 21:35:31),
 UserTransaction(type=trade, created_datetime=2016-04-21 13:19:35),
 ...,
 ]

>>> utx[0].type
'trade'
>>> utx[0].btc
Decimal('0.00981097')
>>> txs[0].btc_mxn
Decimal('7780.00')
>>> txs[0].rate
Decimal('7780.00')


```

### Open Orders ###

```python
## Returns a list of the user’s open orders
## Parameters
## [book = 'btc_mxn'] - Specifies which book to use
##                    - str
>>> oo = api.open_orders()
>>> oo
[Order(order_id=s5ntlud6oupippk8iigw5dazjdxwq5vibjcwdp32ksk9i4h0nyxsc8svlpscuov5, type=buy, price=7000.00, amount=0.01000000, created_datetime=2016-04-22 14:31:10)]
>>> oo[0].price
Decimal('7000.00')
>>> oo[0].order_id
s5ntlud6oupippk8iigw5dazjdxwq5vibjcwdp32ksl9i4h0nyxsc8svlpscuov5

```

### Lookup Order ###

```python
## Returns a list of details for 1 or more orders
## Parameters
## order_ids -  A list of Bitso Order IDs.
##          - string
>>> orders = api.lookup_order([ORDER_ID1, ORDER_ID2])
>>> orders
[Order(order_id=s0ntlud6oupippk8iigw5dazjdxwq5vibjcwdp12ksk9i4h0nyxsc8svlpscuov5, type=buy, price=7000.00, amount=0.01000000, created_datetime=2016-04-22 14:31:10),
 Order(order_id=whtyptv0f348fajdydoswcf6cj20d0kahd77657l7ctnnd1lrpdn2suebwfpxz0f, type=buy, price=7200.00, amount=0.01200000, created_datetime=2016-04-22 14:32:10)]
```

### Cancel Order ###

```python
## Cancels an open order
## Parameters
## order_id -  A Bitso Order ID.
##          - string
>>> api.cancel_order(ORDER_ID)
u'true' #on success
```

### Buy Limit Order ###

```python
## Places a buy limit order.
## amount - Amount of major currency to buy.
##        - string
## price  - Specified price for the limit order.
##        - string
## [book = 'btc_mxn'] - Specifies which book to use
##                    - str
>>> order = api.buy(amount='.01', price='7000.00')
>>> order
Order(order_id=0zx3f7b8k5jrx1vj123y4nfkd9sguihvhfywm957epycqtvsvzq0m6k0fdgavy5d, type=buy, price=7000.00, amount=0.01000000, created_datetime=2016-04-22 14:43:13)
>>> order.order_id
u'0zx3f7b8k5jrx1vj123y4nfkd9sguihvhfywm957epycqtvsvzq0m6k0fdgavy5d'
>>> order.price
Decimal('7000.00')
>>> order.amount
Decimal('0.01000000')

```

### Sell Order ###

```python
## Places a sell order (both limit and market orders are available)
## amount - 
##        - string
## price  - If supplied, this will place a limit order to sell at the specified price.
##            If not supplied, this will place a market order to sell the amount of major
##            currency specified in amount at the market rate
##        - string
## [book = 'btc_mxn']    - Specifies which book to use
##                       - str
>>> s_order = api.sell(amount='.0032', price='08000')
>>> s_order
Order(order_id=whtyptv0f348fajdydoswcf6cj20d0kahd97647l7ctnnd1lrpdn2suebwfpxz0f, type=sell, price=8000.00, amount=0.00320000, created_datetime=2016-04-22 15:41:00)

```


### Bitcoin Deposit Address ###

```python
## Gets a Bitcoin deposit address to fund your account
>>> api.btc_deposit_address()
u'3CEWgs1goBbafUoThjWff4oX4wQKfxqpeV'
## Returns a Bitcoin address
```


### Bitcoin Withdrawal ###

```python
## Triggers a bitcoin withdrawal from your account
## amount  - The amount of BTC to withdraw from your account
##         - string
## address - The Bitcoin address to send the amount to
##         - string
>>> api.bitcoin_withdrawal('1.10', '1TVXn5ajmMQEbkiYNobgHVutVtMWcNZGV')
ok   # Returns 'ok' on success
```


### Ripple Withdrawal ###

```python
## Triggers a ripple withdrawal from your account
## amount  - The amount of BTC to withdraw from your account
##         - string
## address - The ripple address to send the amount to
##         - string
>>> api.ripple_withdrawal('1.10', 'rG1QQv2nh2gr7RCZ1P8YYcBUKCCN633jCn')
ok   # Returns 'ok' on success
```



### Bank Withdrawal (SPEI) ###

```python
## Triggers a SPEI withdrawal from your account. These withdrawals are
##   immediate during banking hours (M-F 9:00AM - 5:00PM Mexico City Time).
##
## amount  - The amount of MXN to withdraw from your account
##         - string
## recipient_given_names - The recipient’s first and middle name(s)
##         - string
## recipient_family_names - The recipient’s last name)
##         - string
## clabe - The CLABE number where the funds will be sent to
##         - string
## notes_ref - The alpha-numeric reference number for this SPEI
##         - string
## numeric_ref - The numeric reference for this SPEI
##         - string


>>> api.mxn_withdrawal(amount='3500.0', first_names='Satoshi', last_names='Nakamoto', clabe=CLABE, notes_ref=NOTES_REF, numeric_ref=NUMERIC_REF)
ok   # Returns 'ok' on success
```



# Transfer API #

**Access to this API is available on request, and not enabled by default. Users won’t be able to use this API unless Bitso has enabled it on their account. [API Docs](https://bitso.com/api_info/?shell#transfer-api5)**

Bitso’s powerful Transfer API allows for simple integration for routing Bitcoin payments directly through to a choice of Mexican Peso end-points.

The workflow is as follows:

```python
## Request quote
>>> quote = api.transfer_quote(amount='25.0', currency='MXN')
## Create transfer using quote
>>> transfer = api.transfer_create(amount='25.0', currency='MXN', rate=quote.rate, payment_outlet='vo', email_address='mario@ret.io', recipient_given_name='mario romero')
## Send bitcoins to address given
>>> print transfer.wallet_address
## Check Transfer status, after 1 confirmation, pesos are delivered
>>> print api.transfer_status(transfer.id).status
u'confirming'
```

### Get Transfer Quote ###

```python
## Get a quote for a transfer for various Bitso Outlets.
##
## btc_amount  - Mutually exclusive with amount. Either this, or amount should
##               be present in the request. The total amount in Bitcoins, as
##               provided by the user. NOTE: The amount is in BTC format
##               (900mbtc = .9 BTC).
##         - string
## amount  - Mutually exclusive with btc_amount. Either this, or btc_amount
##           should be present in the request. The total amount in Fiat currency.
##           Use this if you prefer specifying amounts in fiat instead of BTC.
##         - string
## currency - An ISO 4217 fiat currency symbol (ie, "MXN"). If btc_amount is
##            provided instead of amount, this is the currency to which the BTC
##            price will be converted into. Otherwise, if amount is specified
##            instead of btc_amount, this is the currency of the specified amount.
##         - string

>>> quote = api.transfer_quote(amount='25.0', currency='MXN')
>>> print quote
TransactionQuote(btc_amount=0.00328834, currency=MXN, rate=7602.60, created_at=2016-05-03 00:33:06, expires_at=2016-05-03 00:34:06, gross=25.00)
>>> quote.btc_amount
Decimal('0.00328834')
>>> quote.outlets.keys()
[u'sp', u'rp', u'vo', u'bw', u'pm']
>>> quote.outlets['vo']
{u'available': True,
 u'daily_limit': Decimal('0.00'),
 u'fee': Decimal('0.00'),
 u'id': u'vo',
 u'maximum_transaction': Decimal('9999.00'),
 u'minimum_transaction': Decimal('25.00'),
 u'name': u'Voucher',
 u'net': Decimal('25.00'),
 u'optional_fields': [],
 u'required_fields': {u'email_address': {u'id': u'email_address',
   u'name': u'Email Address'},
  u'recipient_given_name': {u'id': u'recipient_given_name', u'name': u''}},
 u'verification_level_requirement': u'0'}

```

### Create Transfer ###

```python
## Get a quote for a transfer for various Bitso Outlets.
##
## btc_amount  - Mutually exclusive with amount. Either this, or amount should
##               be present in the request. The total amount in Bitcoins, as
##               provided by the user. NOTE: The amount is in BTC format
##               (900mbtc = .9 BTC).
##         - string
## amount  - Mutually exclusive with btc_amount. Either this, or btc_amount
##           should be present in the request. The total amount in Fiat currency.
##           Use this if you prefer specifying amounts in fiat instead of BTC.
##         - string
## currency - An ISO 4217 fiat currency symbol (ie, "MXN"). If btc_amount is
##            provided instead of amount, this is the currency to which the BTC
##            price will be converted into. Otherwise, if amount is specified
##            instead of btc_amount, this is the currency of the specified amount.
##         - string
## rate - This is the rate (e.g. BTC/MXN), as acquired from the
##        transfer_quote method. You must request a quote in this way before
##        creating a transfer.
##      - string
## payment_outlet - The outlet_id as provided by quote method.
##      - string
## required fields parameters - Each of the other 'required_fields', 
##                              as stipulated in the TransferQuote for the chosen payment_outlet.
##      - string

>>> transfer = api.transfer_create(amount='25.0', currency='MXN', rate=quote.rate, payment_outlet='vo', email_address='satoshin@gmx.com', recipient_given_name='satoshi nakamoto')
>>> print transfer
TransactionQuote(btc_amount=0.00328834, currency=MXN, rate=7602.60, created_at=2016-05-03 00:33:06, expires_at=2016-05-03 00:34:06, gross=25.00)
>>> transfer.btc_amount
Decimal('0.00328834')
>>> quote.wallet_address
u'3LiLpKyfXJmeDcD5ABGtmHGjkxnZTHnBxv'}

```


### Get Transfer Status ###

```python
## Request status for a transfer order 
##
## transfer_id  - Bitso Transfer Order ID (As returned by transfer_create
##                method.
##         - string

>>> print api.transfer_status(transfer.id).status
u'confirming'

```
# Websocket API #

WebSocket is a protocol providing full-duplex communication channels over a single TCP connection. [Bitso's Websocket API](https://bitso.com/api_info/?shell#websocket-api) allows a continuous connection that will receive updates according to the client's subscribed channels.

#### Available Channels: ####
+ **'trades':** will send updates on each new registered trade.
+ **'diff-orders':** will send across any modifications to the order book. Specifically, any state changes in existing orders (including orders not in the top 20), and any new orders.
+ **'orders':** maintains an up-to-date list of the top 20 asks and the top 20 bids, new updates are sent across the channel whenever there is a change in either top 20.

#### Basic Example ####
Prints every trade.
```python
from bitso import websocket


class BasicBitsoListener(websocket.Listener):
    def on_connect(self):
        print "Connected"
        
    def on_update(self, data):
        for obj in data.updates:
            print obj
        
if __name__ == '__main__':
    listener = BasicBitsoListener()
    client = websocket.Client(listener)
    channels = ['trades']
    client.connect(channels)

```

```shell
> python examples/ws_trades.py
Connected
TradeUpdate(tid=96093, amount=0.00296048, rate=8444.56,value=25)
TradeUpdate(tid=96094, amount=0.0568058, rate=8444.56,value=479.7)
TradeUpdate(tid=96095, amount=0.45721742, rate=8444.56,value=3861)
TradeUpdate(tid=96096, amount=1.25176796, rate=8335.88,value=10434.58)
TradeUpdate(tid=96097, amount=0.75948406, rate=8335.83,value=6330.93)
TradeUpdate(tid=96098, amount=0.38027314, rate=8334.31,value=3169.31)
TradeUpdate(tid=96099, amount=0.54340182, rate=8329.95,value=4526.5)
TradeUpdate(tid=96100, amount=0.44632784, rate=8323.59,value=3715.04)
TradeUpdate(tid=96101, amount=0.03216174, rate=8322.31,value=267.65)
TradeUpdate(tid=96102, amount=2.92387591, rate=8318.13,value=24321.17)
TradeUpdate(tid=96103, amount=0.27482146, rate=8313.96,value=2284.85)
TradeUpdate(tid=96104, amount=1.33065393, rate=8312,value=11060.39)
TradeUpdate(tid=96105, amount=0.70166614, rate=8310.66,value=5831.3)
TradeUpdate(tid=96106, amount=0.11416146, rate=8434.37,value=962.88)
```

#### Advanced Example ####
Gets a copy of the order book via the rest API once, and keeps it up to date using the **'diff-orders'** channel. Logs every order, spread update, or trade.

See [examples/livebookexample.py](https://github.com/bitsoex/bitso-py/blob/master/examples/livebookexample.py)

```shell
> python examples/livebookexample.py
2016-05-09 20:17:32,232 - INFO - Starting new HTTPS connection (1): bitso.com
2016-05-09 20:17:33,118 - INFO - Order Book Fetched. Best ask: 8434.3700, Best bid: 8351.3000, Spread: 83.0700
2016-05-09 20:17:33,589 - INFO - Websocket Connection Established
2016-05-09 20:17:33,711 - INFO - Best ask: 8434.3700, Best bid: 8351.3000, Spread: 83.0700
2016-05-09 20:22:30,301 - INFO - New Order. ask: 0.0000 @ 8434.3700 = 0.0000
2016-05-09 20:22:30,306 - INFO - Removed price level at: 8434.3700
2016-05-09 20:22:30,306 - INFO - Best ask: 8440.0000, Best bid: 8351.3000, Spread: 88.7000
2016-05-09 20:22:31,021 - INFO - New Order. ask: 0.1000 @ 8492.9700 = 849.2900
2016-05-09 20:22:31,022 - INFO - Best ask: 8440.0000, Best bid: 8351.3000, Spread: 88.7000
```


# Models #

The wrapper uses models to represent data structures returned by the Bitso API. 


### bitso.Ticker
Atribute | Type | Description | Units
------------ | ------------- | ------------- | -------------
ask | Decimal | Lowest sell order | Minor/Major
bid | Decimal | Highest buy order | Minor/Major
last | Decimal | Last traded price | Minor/Major
high | Decimal | Last 24 hours price high | Minor/Major
low | Decimal | Last 24 hours price low | Minor/Major
vwap | Decimal | Last 24 hours price high | Minor/Major
volume | Decimal | Last 24 hours volume | Major
datetime | Datetime | Ticker current datetime | 
timestamp | String | Ticker current timestamp | Unix timestamp


### bitso.OrderBook
Atribute | Type | Description | Units
------------ | ------------- | ------------- | -------------
asks | List | List of open asks | Minor/Major
bids | List | List of open bids | Minor/Major
datetime | Datetime | OrderBook current datetime | 
timestamp | String | OrderBook current timestamp | Unix timestamp


### bitso.Balance
Atribute | Type | Description | Units
------------ | ------------- | ------------- | -------------
btc_balance | Decimal | BTC balance | BTC
btc_available | Decimal | BTC available for trading (balance - reserved) | BTC
btc_reserved | Decimal | BTC locked in open orders | BTC
mxn_balance | Decimal | MXN balance | MXN
mxn_available | Decimal | MXN available for trading (balance - reserved) | MXN
mxn_reserved | Decimal | MXN locked in open orders | MXN
fee | Decimal | Customer trading fee as a percentage | 


### bitso.Transaction
Atribute | Type | Description | Units
------------ | ------------- | ------------- | -------------
tid | Long | Transaction ID | 
amount | Decimal | Major amount transacted | Major
price | Decimal | Price per unit of major | Minor
side | Decimal | Indicates the maker order side (maker order is the order that was open on the order book) | 
datetime | Datetime | 
timestamp | String | MXN balance | Unix timestamp


### bitso.UserTransaction
Atribute | Type | Description | Units
------------ | ------------- | ------------- | -------------
tid | Long | Unique identifier (only for trades) | 
type | String | Transaction type ('deposit', 'withdrawal', 'trade') |
order_id | String | A 64 character long hexadecimal string representing the order that was fully or partially filled (only for trades) | 
rate | Decimal | Price per minor (only for trades) | Minor
created_datetime | Datetime | Date and time | 
(minor currency code) | Decimal | The minor currency amount | Minor
(major currency code) | Decimal | The major currency amount | Major 


### bitso.Order

Atribute | Type | Description | Units
------------ | ------------- | ------------- | -------------
order_id | String | The Order ID | 
type | String | Order Type ('buy','sell') | 
book | String | Which orderbook the order belongs to (not shown when status = 0) | 
amount | Decimal | The order’s major currency amounts | Major
price | Decimal | The order’s price | Minor
status | String | The order’s status ('cancelled', 'active','partially filled', 'complete') | 
created_datetime | Datetime | The date the order was created | 
updated_datetime | Datetime | The date the order was last updated (not shown when status = 0) | 


### bitso.TransactionQuote

Atribute | Type | Description | Units
------------ | ------------- | ------------- | -------------
btc_amount | Decimal | The total amount in Bitcoins | Major
currency | String | An ISO 4217 fiat currency symbol (ie, “MXN”). | 
gross | Decimal |  | 
rate | Decimal | This major/manor rate (e.g. BTC/MXN) | 
outlets | Dictionary | Dictionary of Bitso Outlet options | 
created_at | Datetime | The date the quote was created | 
expires_at | Datetime | The date the quote will expire | 
success | Bool | quote generated successfully | 


### bitso.TransactionOrder

Atribute | Type | Description | Units
------------ | ------------- | ------------- | -------------
btc_amount | Decimal | The total amount in BTC | BTC
btc_pending | Decimal | Unconfirmed BTC, seen by Bitso servers  | BTC
btc_received | Decimal | Confirmed BTC seen by Bitso servers | BTC
confirmation_code | String | | 
currency | String | An ISO 4217 fiat currency symbol (ie, “MXN”). | 
currency_amount | Decimal | | 
currency_settled | Decimal | | 
currency_fees | Decimal | | 
fields | Dictionary | Required fields for Pyament Outlet | 
created_at | Datetime | The date the transfer was created | 
expires_at | Datetime | The date the transfer order will expire | 
id | String | Transfer Order ID | 
payment_outlet_id | String | Payment Outlet ID | 
qr_img_uri | String | Bitcoin payment QR Code URI | 
user_uri | String | Transfer Order URI | 
wallet_address | Bitcoin address you will send BTC to | 
success | Bool | Response Success | 


### bitso.models.OrderUpdate

Atribute | Type | Description | Units
------------ | ------------- | ------------- | -------------
datetime | Datetime | Order Date/Time | 
timestamp | String | Order Timestamp | Unix Timestamp
side | String | 'bid','ask' | Market side 
rate | Decimal | Order price | Minor
amount | Decimal | Major currency amount | Major
value | Decimal | Total Order Value (amount*rate) | Minor 

### bitso.models.TradeUpdate

Atribute | Type | Description | Units
------------ | ------------- | ------------- | -------------
tid | Int | Trade ID | 
rate | Decimal | Order price | Minor
amount | Decimal | Major currency amount | Major
value | Decimal | Total Order Value (amount*rate) | Minor 

### bitso.models.StreamUpdate

Atribute | Type | Description | Units
------------ | ------------- | ------------- | -------------
channel | String | ('diff-orders', 'trades', 'orders') | 
updates | List | List of (TradeUpdate or OrderUpdate) objects | 


# Notations #

**Major** denotes the cryptocurrency, in our case Bitcoin (BTC).

**Minor** denotes fiat currencies such as Mexican Peso (MXN), etc

An order book is always referred to in the API as “Major_Minor”. For example: “**btc_mxn**”


# Licence #

The MIT License (MIT)

