#!/usr/bin/env python

#
#The MIT License (MIT)
#
#Copyright (c) 2016 Mario Romero 
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


from decimal import Decimal
from datetime import datetime


class BaseModel(object):

    """ Base class for other models. """
    
    def __init__(self, **kwargs):
        self._default_params = {}

    @classmethod
    def _NewFromJsonDict(cls, data, **kwargs):
        if kwargs:
            for key, val in kwargs.items():
                data[key] = val
        return cls(**data)



class Ticker(BaseModel):

    """ A class that represents a Bitso ticker. """
    
    def __init__(self, **kwargs):
        self._default_params = {
            'ask': Decimal(kwargs.get('ask')),
            'bid': Decimal(kwargs.get('bid')),
            'high': Decimal(kwargs.get('high')),
            'last': Decimal(kwargs.get('last')),
            'low': Decimal(kwargs.get('low')),
            'vwap': Decimal(kwargs.get('vwap')),
            'timestamp': kwargs.get('timestamp'),
            'datetime': datetime.fromtimestamp(int(kwargs.get('timestamp'))),
        }
        
        for (param, val) in self._default_params.items():
            setattr(self, param, val)

    def __repr__(self):
        return "Ticker(ask={ask}, bid={bid}, high={high}, last={last}, low={low}, datetime={datetime}, vwaplow={vwap})".format(
            ask=self.ask,
            bid=self.bid,
            high=self.high,
            low=self.low,
            last=self.last,
            vwap=self.vwap,
            datetime=self.datetime)



class OrderBook(BaseModel):

    """ A class that represents a Bitso order book. """
    
    def __init__(self, **kwargs):
        self._default_params = {
            'asks': kwargs.get('asks'),
            'bids': kwargs.get('bids'),
            'timestamp': kwargs.get('timestamp'),
            'datetime': datetime.fromtimestamp(int(kwargs.get('timestamp')))
        }

        for (param, val) in self._default_params.items():
            if param in ['asks', 'bids']:
                parsed_asks = []
                for ask in val:
                    parsed_asks.append({'price': Decimal(ask[0]), 'amount': Decimal(ask[1])})
                setattr(self, param, parsed_asks)
                continue
            setattr(self, param, val)


    def __repr__(self):
        return "OrderBook({num_asks} asks, {num_bids} bids, timestamp={timestamp})".format(
            num_asks=len(self.asks),
            num_bids=len(self.bids),
            timestamp=self.timestamp)



   


class Balance(BaseModel):
        
    """ A class that represents a Bitso user's balance. """

    
    def __init__(self, **kwargs):
        self._default_params = {
            'btc_available': Decimal(kwargs.get('btc_available')),            
            'btc_balance': Decimal(kwargs.get('btc_balance')),
            'btc_reserved': Decimal(kwargs.get('btc_reserved')),
            'mxn_available': Decimal(kwargs.get('mxn_available')),
            'mxn_balance': Decimal(kwargs.get('mxn_balance')),
            'mxn_reserved': Decimal(kwargs.get('mxn_reserved')),
            'fee': Decimal(kwargs.get('fee')),
        }

        for (param, val) in self._default_params.items():
            setattr(self, param, val)
            
    def __repr__(self):
        return "Balance(btc_available={btc_available}, btc_balance={btc_balance}, btc_reserved={btc_reserved}, mxn_available={mxn_available}, mxn_balance={mxn_balance}, mxn_reserved={mxn_reserved}, fee={fee})".format(
            btc_available=self.btc_available,
            btc_balance=self.btc_balance,
            btc_reserved=self.btc_reserved,
            mxn_available=self.mxn_available,
            mxn_balance=self.mxn_balance,
            mxn_reserved=self.mxn_reserved,
            fee=self.fee)
    
            
class Transaction(BaseModel):

    """ A class that represents a Bitso public trade transaction. """

    
    def __init__(self, **kwargs):
        self._default_params = {
            'tid': kwargs.get('tid'),
            'amount': Decimal(kwargs.get('amount')),
            'price': Decimal(kwargs.get('price')),
            'side': kwargs.get('side'),
            'timestamp': kwargs.get('date'),
            'datetime':  datetime.fromtimestamp(int(kwargs.get('date')))

            
        }

        for (param, val) in self._default_params.items():
            setattr(self, param, val)

    def __repr__(self):
        return "Transaction(tid={tid}, price={price}, amount={amount}, side={side}, datetime={datetime})".format(
            tid=self.tid,
            price=self.price,
            amount=self.amount,
            side=self.side,
            datetime=self.datetime)

   
            
class UserTransaction(BaseModel):

    """ A class that represents a transaction for a Bitso user. """

        
    def __init__(self, **kwargs):
        self._type_mappings = {
            0: 'deposit',
            1: 'withdrawal',
            2: 'trade'
        }

        for (param, value) in kwargs.items():
            if param == 'id':
                param = 'tid'
            elif param == 'type':
                value = self._type_mappings.get(value,value)
            elif param == 'datetime':
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                param = 'created_datetime'
            elif param in ('btc', 'mxn', 'rate'):
                value = Decimal(value)
            setattr(self, param, value)

    def __repr__(self):
        return "UserTransaction(type={tx_type}, created_datetime={created_datetime})".format(
            tx_type=self.type,
            created_datetime=self.created_datetime)




class Order(BaseModel):

    """ A class that represents a Bitso order. """

        
    def __init__(self, **kwargs):
        self._status_mappings = {
            '-1': 'cancelled',
            '0': 'active',
            '1': 'partial',
            '2': 'complete'
        }
        
        self._type_mappings = {
            '0': 'buy',
            '1': 'sell'
        }

        for (param, value) in kwargs.items():
            if param == 'datetime':
                param = 'created_datetime'
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            elif param in ['created', 'updated']:
                param = param + '_datetime'
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            elif param == 'id':
                param = 'order_id'
            elif param == 'status':
                value = self._status_mappings.get(value,value)
            elif param == 'type':
                value = self._type_mappings.get(value,value)
            elif param == 'price':
                if Decimal(value) == 0.0:
                    value = None
                else:
                    value = Decimal(value)
            elif param == 'amount':
                value = Decimal(value)
            setattr(self, param, value)
            
    def __repr__(self):
        return "Order(order_id={order_id}, type={order_type}, price={price}, amount={amount}, created_datetime={created_datetime})".format(
            order_id=self.order_id,
            order_type=self.type,
            price=self.price,
            amount=self.amount,
            created_datetime=self.created_datetime)
