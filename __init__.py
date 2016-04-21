
import time
import hmac
import hashlib
import json
import requests
from urllib import urlencode

class ApiError(Exception):
    pass

class ApiClientError(Exception):
    pass
    

class Api(object):
    def __init__(self, client_id=None, key=None, secret=None):
        self.base_url = "https://bitso.com/api/v2"
        self.client_id = client_id
        self.key = key
        self._secret = secret

    def ticker(self, book=None):
        url = '%s/ticker' % self.base_url
        parameters = {}
        if book:
            parameters['book'] = book
        resp = self._request_url(url, 'GET', params=parameters)
        return Ticker._NewFromJsonDict(resp)


    def order_book(self, book=None, group=None):
        url = '%s/order_book' % self.base_url
        parameters = {}
        if book:
            parameters['book'] = book
        if group:
            parameters['group'] = group
        resp = self._request_url(url, 'GET', params=parameters)
        return OrderBook._NewFromJsonDict(resp)


    def transactions(self, book=None, time=None):
        url = '%s/transactions' % self.base_url
        parameters = {}
        if book:
            parameters['book'] = book
        if time:
            parameters['time'] = time
        resp = self._request_url(url, 'GET', params=parameters)
        return [Transaction._NewFromJsonDict(x) for x in resp]

    def balance(self):
        url = '%s/balance' % self.base_url
        parameters = self._build_auth_payload()
        resp = self._request_url(url, 'POST', params=parameters)
        return Balance._NewFromJsonDict(resp) 


    def user_transactions(self, offset=None, limit=None, sort=None, book=None):
        url = '%s/user_transactions' % self.base_url
        parameters = self._build_auth_payload()
        if offset:
            parameters['offset'] = offset
        if limit:
            parameters['limit'] = limit
        if sort:
            parameters['sort'] = sort
        if book:
            parameters['book'] = book
        resp = self._request_url(url, 'POST', params=parameters)
        return [UserTransaction._NewFromJsonDict(x) for x in resp]

    def open_orders(self, book=None):
        url = '%s/open_orders' % self.base_url
        parameters = self._build_auth_payload()
        if book:
            parameters['book'] = book
        resp = self._request_url(url, 'POST', params=parameters)
        return [Order._NewFromJsonDict(x) for x in resp]


    def lookup_order(self, order_ids):
        url = '%s/lookup_order' % self.base_url
        if isinstance(order_ids, basestring):
            order_ids = [order_ids]
        parameters = self._build_auth_payload()
        #parameters['id'] = ','.join(order_ids)
        parameters['id[]'] = order_ids
        resp = self._request_url(url, 'POST', params=parameters)
        return [Order._NewFromJsonDict(x) for x in resp]

    def cancel_order(self, order_id):
        url = '%s/cancel_order' % self.base_url
        parameters = self._build_auth_payload()
        parameters['id'] = order_id
        resp = self._request_url(url, 'POST', params=parameters)
        return resp

    def buy(self, amount=None, price=None, book=None):
        if amount is None:
            raise ApiClientError({u'message': u'amount not specified.'})
        url = '%s/buy' % self.base_url
        parameters = self._build_auth_payload()
        parameters['amount'] = str(amount).encode('utf-8')
        if price is not None:
            parameters['price'] = str(price).encode('utf-8')
        parameters['book'] = book
        resp = self._request_url(url, 'POST', params=parameters)
        return Order._NewFromJsonDict(resp) 


    def sell(self, amount=None, price=None, book=None):
        if amount is None:
            raise ApiClientError({u'message': u'amount not specified.'})
        url = '%s/sell' % self.base_url
        parameters = self._build_auth_payload()
        parameters['amount'] = str(amount).encode('utf-8')
        if price is not None:
            parameters['price'] = str(price).encode('utf-8')
        parameters['book'] = book
        resp = self._request_url(url, 'POST', params=parameters)
        return Order._NewFromJsonDict(resp) 


    def btc_deposit_address(self):
        url = '%s/bitcoin_deposit_address' % self.base_url
        parameters = self._build_auth_payload()
        resp = self._request_url(url, 'POST', params=parameters)
        return resp

    def btc_withdrawal(self, amount, address):
        url = '%s/bitcoin_withdrawal' % self.base_url
        parameters = self._build_auth_payload()
        parameters['amount'] = str(amount).encode('utf-8')
        parameters['address'] = address
        resp = self._request_url(url, 'POST', params=parameters)
        return resp

    def mxn_withdrawal(self, amount=None, first_names=None, last_names=None, clabe=None, notes_ref=None, numeric_ref=None):
        url = '%s/spei_withdrawal' % self.base_url
        parameters = self._build_auth_payload()
        parameters['amount'] = str(amount).encode('utf-8')
        parameters['recipient_given_names'] = first_names
        parameters['recipient_family_names'] = last_names
        parameters['clabe'] = clabe
        parameters['notes_ref'] = notes_ref
        parameters['numeric_ref'] = numeric_ref
        resp = self._request_url(url, 'POST', params=parameters)
        return resp


    def _build_auth_payload(self):
        parameters = {}
        parameters['key'] = self.key
        parameters['nonce'] = str(int(time.time()))
        msg_concat = parameters['nonce']+self.client_id+self.key
        parameters['signature'] = hmac.new(self._secret.encode('utf-8'),
                                           msg_concat.encode('utf-8'),
                                           hashlib.sha256).hexdigest()
        return parameters

    def _request_url(self, url, verb, params=None):
        url = self._build_url(url, params)        
        if verb == 'GET':
            try:
                resp = requests.get(url)
            except requests.RequestException as e:
                raise
        elif verb == 'POST':
            try:
                resp = requests.post(url, data=params)
            except requests.RequestException as e:
                raise
        data = self._parse_json(resp.content.decode('utf-8'))
        return data

    def _build_url(self, url, params):
        if params and len(params) > 0:
            url = url+'?'+self._encode_parameters(params)
        print url
        return url

    def _encode_parameters(self, parameters):
        if parameters is None:
            return None
        else:
            param_tuples = []
            for k,v in parameters.items():
                if v is None:
                    continue
                if isinstance(v, (list, tuple)):
                    for single_v in v:
                        param_tuples.append((k, single_v))
                else:
                    param_tuples.append((k,v))
            return urlencode(param_tuples)


         
    def _parse_json(self, json_data):
        try:
            data = json.loads(json_data)
            self._check_for_api_error(data)
        except:
            raise
        return data

    def _check_for_api_error(self, data):
        if 'error' in data:
            raise ApiError(data['error'])
        if isinstance(data, (list, tuple)) and len(data)>0:
            if 'error' in data[0]:
                raise ApiError(data[0]['error'])
        


class BaseModel(object):
    def __init__(self, **kwargs):
        self._default_params = {}

    @classmethod
    def _NewFromJsonDict(cls, data, **kwargs):
        if kwargs:
            for key, val in kwargs.items():
                data[key] = val
        return cls(**data)

        

class Ticker(BaseModel):
    def __init__(self, **kwargs):
        self._default_params = {
            'ask': None,
            'bid': None,
            'high': None,
            'last': None,
            'low': None,
            'timestamp': None,
            'vwap': None,
        }
        for (param, default) in self._default_params.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "Ticker(ask={ask}, bid={bid}, high={high}, last={last}, low={low}, timestamp={timestamp}, vwaplow={vwap})".format(
            ask=self.ask,
            bid=self.bid,
            high=self.high,
            low=self.low,
            last=self.last,
            vwap=self.vwap,
            timestamp=self.timestamp)

            
class OrderBook(BaseModel):
    def __init__(self, **kwargs):
        self._default_params = {
            'asks': None,
            'bids': None,
            'timestamp': None,
        }

        for (param, default) in self._default_params.items():
            setattr(self, param, kwargs.get(param, default))


    def __repr__(self):
        return "OrderBook({num_asks} asks, {num_bids} bids, timestamp={timestamp})".format(
            num_asks=len(self.asks),
            num_bids=len(self.bids),
            timestamp=self.timestamp)

            
class Transaction(BaseModel):
    def __init__(self, **kwargs):
        self._default_params = {
            'date': None,
            'amount': None,
            'side': None,
            'price': None,
            'tid': None,
        }

        for (param, default) in self._default_params.items():
            setattr(self, param, kwargs.get(param, default))


    def __repr__(self):
        return "Ticker(ask={ask}, bid={bid}, high={high}, last={last}, low={low}, timestamp={timestamp}, vwaplow={vwap})".format(
            ask=self.ask,
            bid=self.bid,
            high=self.high,
            low=self.low,
            last=self.last,
            vwap=self.vwap,
            timestamp=self.timestamp)



class Balance(BaseModel):
    def __init__(self, **kwargs):
        self._default_params = {
            'btc_available': None,            
            'btc_balance': None,
            'btc_reserved': None,
            'mxn_available': None,
            'mxn_balance': None,
            'mxn_reserved': None,
            'fee': None,
        }

        for (param, default) in self._default_params.items():
            setattr(self, param, kwargs.get(param, default))

    def __repr__(self):
        return "Balance(btc_available={btc_available}, btc_balance={btc_balance}, btc_reserved={btc_reserved}, mxn_available={mxn_available}, mxn_balance={mxn_balance}, mxn_reserved={mxn_reserved}, fee={fee})".format(
            btc_available=self.btc_available,
            btc_balance=self.btc_balance,
            btc_reserved=self.btc_reserved,
            mxn_available=self.mxn_avaUsilable,
            mxn_balance=self.mxn_balance,
            mxn_reserved=self.mxn_reserved,
            fee=self.fee)
        
            
class UserTransaction(BaseModel):
    def __init__(self, **kwargs):
        self._type_mappings = {
            0: 'deposit',
            1: 'withdrawal',
            2: 'trade'
        }

        for (param, value) in kwargs.items():
            if param == 'id':
                param = 'transaction_id'
            elif param == 'type':
                value = self._type_mappings.get(value,value)
            elif param == 'datetime':
                param = 'created'
            setattr(self, param, value)

    def __repr__(self):
        return "UserTransaction(type={tx_type}, created={created})".format(
            tx_type=self.type,
            created=self.created)
        

class Order(BaseModel):
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
                param = 'created'
            elif param == 'id':
                param = 'order_id'
            elif param == 'status':
                value = self._status_mappings.get(value,value)
            elif param == 'type':
                value = self._type_mappings.get(value,value)
            elif param == 'price' and float(value) == 0.0:
                print "value"
                print value
                value = None
            setattr(self, param, value)
            
    def __repr__(self):
        return "Order(order_id={order_id}, type={order_type}, price={price}, amount={amount}, created={created})".format(
            order_id=self.order_id,
            order_type=self.type,
            price=self.price,
            amount=self.amount,
            created=self.created)
