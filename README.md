# python-bitso #

A python wrapper for the [Bitso API](https://bitso.com/api_info/) 


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


## Public calls (no API authorisation needed) ##

### Ticker ###

```python
# Ticker information
 >>>  api.ticker()
{
	'last': decimal,                 # Last traded price
	'high': decimal,                # Last 24 hours price high
	'low': decimal,                  # Last 24 hours price low
	'vwap': decimal,               # Last 24 hours volume weighted average price
	'volume': decimal,           # Last 24 hours volume
	'bid': decimal,                  # Highest buy order
    'ask': decimal                  # Lowest sell order
    'timestamp': string,         # Current unix timestamp
	'datetime': datetime,        # Current datetime
    
}
```

### Order Book ###

```python
# Public order book
# Parameters
## [group = btc_mxn] - Specifies which book to use
##                - string
## [group = True] - Group orders with the same price
##                - boolean
>>> ob = api.order_book()
>>> print ob.datetime  # datetime object
>>> print ob.bids
[                  
        {
            'price': decimal,   ## Price for bid
            'amount': decimal   ## Amount bid
        }, ...
]

>>> print ob.asks

[                   
        {
            'price': decimal,   ## Price for ask
            'amount': decimal   ## Amount asked
        }, ...
]

```

### Transactions ###

```python
# Public transactions
# Parameters
## [book = 'btc_mxn']    - Specifies which book to use
##                 - str
## [time = 'hour']   - Time frame for transaction export ('hour', 'minute')
##                 - str
>>> txs = api.transactions()
>>> print txs
[Transaction(tid=91314, price=7864.10, amount=0.81446192, side=sell, datetime=2016-04-22 13:47:29),
 Transaction(tid=91313, price=7864.10, amount=0.32061901, side=sell, datetime=2016-04-22 13:36:18),
 Transaction(tid=91312, price=7863.72, amount=0.00357865, side=buy, datetime=2016-04-22 13:34:27),
 Transaction(tid=91311, price=7863.72, amount=0.74986010, side=sell, datetime=2016-04-22 13:34:07),
 ...
 ]

>>> txs[0].price
>>> Decimal('7864.10')
>>> txs[0].amount
>>> Decimal('0.81446192')
>>> txs[0].datetime 
>>> datetime.datetime(2016, 4, 22, 13, 47, 29)

```


## Private calls (authorisation required) ##

Private endpoints are used to manage your account and your orders. These requests must be signed
with your [Bitso credentials](https://bitso.com/api_info#generating-api-keys) 

```python
 >>> import bitso
 >>> api = bitso.Api(CLIENT_ID, API_KEY, API_SECRET)
```

### Account Balance ###

```python
# Your account balance
>>> balance = api.balance()
>>> balance.mxn_balance
>>> Decimal('4834.63')
>>> balance.btc_balance
>>> Decimal('1.01300152')


    'mxn_balance': decimal,     # MXN balance
    'btc_balance': decimal,     # BTC balance
    'mxn_reserved': decimal,    # MXN locked in open orders
    'btc_reserved': decimal,    # BTC locked in open orders
    'mxn_available': decimal,   # MXN available for trading (balance - reserved)
    'btc_available': decimal,   # BTC available for trading (balance - reserved)
    'fee': decimal              # Customer trading fee as a percentag

```

### User Transactions ###

```python
# Your transactions
# Parameters
## [offset = 0]    - Skip that many transactions before beginning to return results
##                 - int
## [limit = 100]   - Limit result to that many transactions
##                 - int
## [sort = 'desc'] - Sorting by datetime
##                 - string - 'asc' or
##                 -        - 'desc'
>>> utx = api.user_transactions()
>>> print utx
[UserTransaction(type=trade, created_datetime=2016-04-21 23:17:39),
 UserTransaction(type=trade, created_datetime=2016-04-21 23:11:39),
 UserTransaction(type=trade, created_datetime=2016-04-21 21:40:07),
 UserTransaction(type=trade, created_datetime=2016-04-21 21:35:31),
 UserTransaction(type=trade, created_datetime=2016-04-21 13:19:35),
 ...,
 ]

>>> utx[0].type
>>> 'trade'
>>> utx[0].btc
>>> Decimal('0.00981097')
>>> txs[0].btc_mxn
>>> Decimal('7780.00')
>>> txs[0].rate
>>> Decimal('7780.00')


```

### Open Orders ###

```python
# Returns a list of the user’s open orders
>>> oo = api.open_orders()
>>> print oo
[Order(order_id=s5ntlud6oupippk8iigw5dazjdxwq5vibjcwdp32ksk9i4h0nyxsc8svlpscuov5, type=buy, price=7000.00, amount=0.01000000, created_datetime=2016-04-22 14:31:10)]
>>> oo[0].price
>>> Decimal('7000.00')
>>> oo[0].order_id
>>> s5ntlud6oupippk8iigw5dazjdxwq5vibjcwdp32ksl9i4h0nyxsc8svlpscuov5

```

### Cancel Order ###

```python
# Cancels an open order
# Parameters
## order_id -  A Bitso Order ID.
##          - string
>>> api.cancel_order(ORDER_ID)
>>> u'true' #on success
```

### Buy Limit Order ###

```python
# Places a buy limit order.
## amount - Amount of major currency to buy.
##        - string
## price  - Specified price for the limit order.
##        - string
## [book = 'btc_mxn']    - Specifies which book to use
##                 - str
>>> order = api.buy(amount='.01', price='7000.00')
>>> order
Order(order_id=0zx3f7b8k5jrx1vj123y4nfkd9sguihvhfywm957epycqtvsvzq0m6k0fdgavy5d, type=buy, price=7000.00, amount=0.01000000, created_datetime=2016-04-22 14:43:13)
>>> order.order_id
>>> u'0zx3f7b8k5jrx1vj123y4nfkd9sguihvhfywm957epycqtvsvzq0m6k0fdgavy5d'
>>> order.price
>>> Decimal('7000.00')
>>> order.amount
>>> Decimal('0.01000000')

```

### Sell Order ###

```python
# Places a sell order (both limit and market orders are available)
## amount - 
##        - string
## price  - If supplied, this will place a limit order to sell at the specified price.
##            If not supplied, this will place a market order to sell the amount of major
##            currency specified in amount at the market rate
##        - string
## [book = 'btc_mxn']    - Specifies which book to use
##                 - str
>>> s_order = api.sell(amount='.0032', price='08000')
>>> s_order
>>> Order(order_id=whtyptv0f348fajdydoswcf6cj20d0kahd97647l7ctnnd1lrpdn2suebwfpxz0f, type=sell, price=8000.00, amount=0.00320000, created_datetime=2016-04-22 15:41:00)

```


### Bitcoin Deposit Address ###

```python
# Gets a Bitcoin deposit address to fund your account
>>> api.btc_deposit_address()
>>> u'3CEWgs1goBbafUoThjWff4oX4wQKfxqpeV'
# Returns a Bitcoin address
```


### Bitcoin Withdrawal ###

```python
# Triggers a bitcoin withdrawal from your account
## amount  - The amount of BTC to withdraw from your account
##         - string
## address - The Bitcoin address we will send the amount to
##         - string
>>> api.bitcoin_withdrawal('1.10', ''CEWgs1goBbafUoThjWff4oX4wQKfxqpeV')
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



### Licence ###

The MIT License (MIT)

Copyright (c) 2016 Mario Romero 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
