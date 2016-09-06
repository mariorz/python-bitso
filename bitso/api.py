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


import hashlib
import hmac
import json
import time
import requests

from urllib import urlencode


from bitso import (ApiError, ApiClientError, Ticker, OrderBook, Balance, Transaction,
                     UserTransaction, Order, TransactionQuote, TransactionOrder, LedgerEntry)


class Api(object):
    """A python interface for the Bitso API

    Example usage:
      To create an instance of the bitso.Api class, without authentication:
      
        >>> import bitso
        >>> api = bitso.Api()
      
      To get the Bitso price ticker:
      
        >>> ticker = api.ticker()
        >>> print ticker.ask
        >>> print ticker.bid

      To use the private endpoints, initiate bitso.Api with a client_id,
      api_key, and api_secret (see https://bitso.com/developers?shell#private-endpoints):
      
        >>> api = bitso.Api(CLIENT_ID, API_KEY, API_SECRET)
        >>> balance = api.balance()
        >>> print balance.btc_available
        >>> print balance.mxn_available
    """
    
    def __init__(self, client_id=None, key=None, secret=None):
        """Instantiate a bitso.Api object.
        
        Args:
          client_id:
            Bitso Client ID
          key:
            Bitso API Key 
          secret:
            Bitso API Secret
        """
        self.base_url = "https://bitso.com/api/v2"
        self.base_url_v3 = "https://bitso.com/api/v3"
        self.client_id = client_id
        self.key = key
        self._secret = secret

    def ticker(self, book=None):
        """Get a Bitso price ticker.

        Args:
          book (str, optional):
            Specifies which book to use. Default is btc_mxn
            
        Returns:
          A bitso.Ticker instance.
        
        """
        url = '%s/ticker' % self.base_url
        parameters = {}
        if book:
            parameters['book'] = book
        resp = self._request_url(url, 'GET', params=parameters)
        return Ticker._NewFromJsonDict(resp)


    def order_book(self, book=None, group=None):
        """Get a public Bitso order book with a 
        list of all open orders in the specified book
        

        Args:
          book (str, optional):
            Specifies which book to use. Default is btc_mxn
          group (bool, optional):
            Specifies if orders with the same price should
            be grouped. Default is True
            
        Returns:
          A bitso.OrderBook instance.
        
        """

        url = '%s/order_book' % self.base_url
        parameters = {}
        if group != None:
            if group == True:
                parameters['group'] = True
            else:
                parameters['group'] = False
        if book:
            parameters['book'] = book
        resp = self._request_url(url, 'GET', params=parameters)
        return OrderBook._NewFromJsonDict(resp)

    def transactions(self, book=None, time=None):
        """Get a list of recent trades from the specified book.

        Args:
          book (str, optional):
            Specifies which book to use. Default is btc_mxn
          time (str, optional):
            Time frame for transaction export ('minute', 'hour')
            Default is 'hour'.
            
        Returns:
          A list of bitso.Transaction instances.        
        """

        url = '%s/transactions' % self.base_url
        parameters = {}
        if book:
            parameters['book'] = book
        if time:
            if time.lower() not in ('minute', 'hour'):
                raise ApiClientError({u'message': u"time is not 'hour' or 'minute'"})
            parameters['time'] = time
        resp = self._request_url(url, 'GET', params=parameters)
        return [Transaction._NewFromJsonDict(x) for x in resp]

    def balance(self):
        """Get a user's balance.

        Args: None

        Returns:
          A bitso.Balance instance.        
        """

        url = '%s/balance' % self.base_url
        parameters = self._build_auth_payload()
        resp = self._request_url(url, 'POST', params=parameters)
        return Balance._NewFromJsonDict(resp) 


    def user_transactions(self, offset=None, limit=None, sort=None, book=None):
        """Get a list of the user's transactions

        Args:
          offset (int, optional):
            Skip that many transactions before beginning to return results.
            Defuault is 0
          limit (int, optional):
            Limit result to that many transactions.
            Defuault is 100
          sort (str, optional):
            Sorting by datetime: 'asc', 'desc'
            Defuault is 'desc'
          book (str, optional):
            Specifies which book to use. Default is btc_mxn

            
        Returns:
          A list bitso.UserTransaction instances.        
        """

        url = '%s/user_transactions' % self.base_url
        parameters = self._build_auth_payload()
        if offset:
            parameters['offset'] = offset
        if limit:
            parameters['limit'] = limit
        if sort:
            if not isinstance(sort, basestring) or sort.lower() not in ['asc', 'desc']:
                 raise ApiClientError({u'message': u"sort is not 'asc' or 'desc' "})
            parameters['sort'] = sort
        if book:
            parameters['book'] = book
        resp = self._request_url(url, 'POST', params=parameters)
        return [UserTransaction._NewFromJsonDict(x) for x in resp]

    def open_orders(self, book=None):
        """Get a list of the user's open orders

        Args:
          book (str, optional):
            Specifies which book to use. Default is btc_mxn
            
        Returns:
          A list of bitso.Order instances.        
        """
        url = '%s/open_orders' % self.base_url
        parameters = self._build_auth_payload()
        if book:
            parameters['book'] = book
        resp = self._request_url(url, 'POST', params=parameters)
        return [Order._NewFromJsonDict(x) for x in resp]


    def lookup_order(self, order_ids):
        """Get a list of details for one or more orders

        Args:
          order_ids (list):
            A list of Bitso Order IDs
            
        Returns:
          A list of bitso.Order instances.        
        """
        url = '%s/lookup_order' % self.base_url
        if isinstance(order_ids, basestring):
            order_ids = [order_ids]
        parameters = self._build_auth_payload()
        parameters['id[]'] = order_ids
        resp = self._request_url(url, 'POST', params=parameters)
        return [Order._NewFromJsonDict(x) for x in resp]

    def cancel_order(self, order_id):
        """Cancels an open order

        Args:
          order_id (str):
            A Bitso Order ID.
            
        Returns:
          true.        
        """
        url = '%s/cancel_order' % self.base_url
        parameters = self._build_auth_payload()
        parameters['id'] = order_id
        resp = self._request_url(url, 'POST', params=parameters)
        return resp

    def buy(self, amount=None, price=None, book=None):
        """Places a buy limit order.

        Args:
          amount (str):
            Amount of major currency to buy. 
          price (str):
            Specified price for the limit order.
          book (str, optional):
            Specifies which book to use. Default is btc_mxn

        Returns:
          A bitso.Order instance.        
        """

        if amount is None:
            raise ApiClientError({u'message': u'amount not specified.'})
        url = '%s/buy' % self.base_url
        parameters = self._build_auth_payload()
        parameters['amount'] = str(amount).encode('utf-8')
        if price is None:
            raise ApiClientError({u'message': u'price not specified.'})
        if price is not None:
            parameters['price'] = str(price).encode('utf-8')
        parameters['book'] = book
        resp = self._request_url(url, 'POST', params=parameters)
        return Order._NewFromJsonDict(resp) 


    def sell(self, amount=None, price=None, book=None):
        """Places a sell order (both limit and market orders are available)

        Args:
          amount (str):
            Amount of major currency to buy. 
          price (str, optional):
            If supplied, this will place a limit order to sell at the specified price.
            If not supplied, this will place a market order to sell the amount of major
            currency specified in amount at the market rate
          book (str, optional):
            Specifies which book to use. Default is btc_mxn

        Returns:
          A bitso.Order instance.        
        """
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
        """Gets a Bitcoin deposit address to fund your account

        Args: None
        
        Returns:
          A Bitcoin address       
        """
        url = '%s/bitcoin_deposit_address' % self.base_url
        parameters = self._build_auth_payload()
        resp = self._request_url(url, 'POST', params=parameters)
        return resp

    def btc_withdrawal(self, amount, address):
        """Triggers a bitcoin withdrawal from your account

        Args:
          amount (str):
            The amount of BTC to withdraw from your account
          address (str):
            The Bitcoin address to send the amount to
        
        Returns:
          ok      
        """

        url = '%s/bitcoin_withdrawal' % self.base_url
        parameters = self._build_auth_payload()
        parameters['amount'] = str(amount).encode('utf-8')
        parameters['address'] = address
        resp = self._request_url(url, 'POST', params=parameters)
        return resp

    def ripple_withdrawal(self, currency, amount, address):
        """Triggers a ripple withdrawal from your account

        Args:
          currency (str):
            The currency to withdraw
          amount (str):
            The amount of BTC to withdraw from your account
          address (str):
            The ripple address to send the amount to
        
        Returns:
          ok      
        """

        url = '%s/ripple_withdrawal' % self.base_url
        parameters = self._build_auth_payload()
        parameters['currency'] = str(currency).encode('utf-8')
        parameters['amount'] = str(amount).encode('utf-8')
        parameters['address'] = address
        resp = self._request_url(url, 'POST', params=parameters)
        return resp

    
    def mxn_withdrawal(self, amount=None, first_names=None, last_names=None, clabe=None, notes_ref=None, numeric_ref=None):
        """Triggers a SPEI withdrawal from your account. These withdrawals are
        immediate during banking hours (M-F 9:00AM - 5:00PM Mexico City Time).

        Args:
          amount (str):
            The amount of MXN to withdraw from your account
          recipient_given_names (str):
            The recipient's first and middle name(s)
          recipient_family_names (str):
            The recipient's last names
          clabe (str):
            The CLABE number where the funds will be sent to
            https://en.wikipedia.org/wiki/CLABE
          notes_ref (str):
            The alpha-numeric reference number for this SPEI
          numeric_ref (str):
            The numeric reference for this SPEI
        
        Returns:
          ok      
        """

        
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


    def transfer_quote(self, amount=None, btc_amount=None, currency=None):
        """Get a quote for a transfer for various Bitso Outlets.

        Args:
          btc_amount (str):
            Mutually exclusive with amount. Either this, or amount should
            be present in the request. The total amount in Bitcoins, as
            provided by the user. NOTE: The amount is in BTC format
            (900mbtc = .9 BTC).
          amount (str):
            Mutually exclusive with btc_amount. Either this, or btc_amount
            should be present in the request. The total amount in Fiat currency.
            Use this if you prefer specifying amounts in fiat instead of BTC.
          currency (str):
            An ISO 4217 fiat currency symbol (ie, "MXN"). If btc_amount is
            provided instead of amount, this is the currency to which the BTC
            price will be converted into. Otherwise, if amount is specified
            instead of btc_amount, this is the currency of the specified amount.
        
        Returns:
          A bitso.TransactionQuote instance.         
        """
        
        if currency is None:
            raise ApiClientError({u'message': u"Currency symbol not specified"})
        if amount is None and btc_amount is None:
            raise ApiClientError({u'message': u"Neither 'amount' nor 'btc_amount' are specified"})
        if amount is not None and btc_amount is not None:
            raise ApiClientError({u'message': u"'amount' and 'btc_amount' are mutually exclusive. Pick one"})
        
        url = '%s/transfer_quote' % self.base_url
        parameters = self._build_auth_payload()
        if amount:
            parameters['amount'] = str(amount).encode('utf-8')
        elif btc_amount:
            parameters['btc_amount'] = str(btc_amount).encode('utf-8')

        parameters['currency'] = currency
        parameters['full'] = True
        resp = self._request_url(url, 'POST', params=parameters)
        return TransactionQuote._NewFromJsonDict(resp) 



    def transfer_create(self,
                        amount=None,
                        btc_amount=None,
                        currency=None,
                        rate = None,
                        payment_outlet=None,
                        **kwargs):
        """Request a currency transfer using quoted Bitso transer outlet

        Args:
          btc_amount (str):
            Mutually exclusive with amount. Either this, or amount should
            be present in the request. The total amount in Bitcoins, as
            provided by the user. NOTE: The amount is in BTC format
            (900mbtc = .9 BTC).
          amount (str):
            Mutually exclusive with btc_amount. Either this, or btc_amount
            should be present in the request. The total amount in Fiat currency.
            Use this if you prefer specifying amounts in fiat instead of BTC.
          currency (str):
            An ISO 4217 fiat currency symbol (ie, "MXN"). If btc_amount is
            provided instead of amount, this is the currency to which the BTC
            price will be converted into. Otherwise, if amount is specified
            instead of btc_amount, this is the currency of the specified amount.
          rate (str):
            This is the rate (e.g. BTC/MXN), as acquired from the
            transfer_quote method. You must request a quote in this way before
            creating a transfer.
          payment_outlet (str):
            The outlet_id as provided by quote method. 
          required fields parameters: (str):
            Each of the other 'required_fields', as stipulated in the TransferQuote
            for the chosen payment_outlet.

        
        Returns:
          A bitso.TransactionQuote instance.         
        """
        
        
        if currency is None:
            raise ApiClientError({u'message': u"'currency' not specified"})
        if amount is None and btc_amount is None:
            raise ApiClientError({u'message': u"Neither 'amount' nor 'btc_amount' are specified"})
        if amount is not None and btc_amount is not None:
            raise ApiClientError({u'message': u"'amount' and 'btc_amount' are mutually exclusive. Pick one"})
        if rate is None:
            raise ApiClientError({u'message': u"'rate' not specified"})
        if payment_outlet is None:
            raise ApiClientError({u'message': u"'payment_outlet' not specified"})


        url = '%s/transfer_create' % self.base_url
        parameters = self._build_auth_payload()
        if amount:
            parameters['amount'] = str(amount).encode('utf-8')
        elif btc_amount:
            parameters['btc_amount'] = str(btc_amount).encode('utf-8')

        parameters['currency'] = currency
        parameters['rate'] = str(rate).encode('utf-8')
        parameters['payment_outlet'] = payment_outlet
        for k, v in kwargs.iteritems():
            parameters[k] = str(v).encode('utf-8')
        resp = self._request_url(url, 'POST', params=parameters)
        return TransactionOrder._NewFromJsonDict(resp) 

             
    def transfer_status(self, transfer_id):
        """Request status for a transfer order 

        Args:
          transfer_id (str):
            Bitso Transfer Order ID (As returned by transfer_create
            method.

        """
        if transfer_id is None:
            raise ApiClientError({u'message': u"'transfer_id' not specified"})
        url = '%s/transfer/%s' % (self.base_url, transfer_id)
        parameters = self._build_auth_payload()
        resp = self._request_url(url, 'GET', params=parameters)
        return TransactionOrder._NewFromJsonDict(resp)

    def ledger(self, operations='', marker=None, limit=25, sort='desc'):
        """Get the ledger of user operations 

        Args:
          operations (str, optional):
            They type of operations to include. Enum of ('trade', 'fee', 'funding', 'withdrawal')
            If None, returns all the operations.
          marker (str, optional):
            Returns objects that are older or newer (depending on 'sort') than the object which
            has the marker value as ID
          limit (int, optional):
            Limit the number of results to parameter value, max=100, default=25
          sort (str, optional):
            Sorting by datetime: 'asc', 'desc'
            Defuault is 'desc'
        """
        url = '%s/ledger/%s' % (self.base_url_v3, operations)
        parameters = self._build_auth_payload()
        if marker:
            parameters['marker'] = marker
        if limit:
            parameters['limit'] = limit
        if sort:
            parameters['sort'] = sort
        resp = self._request_url(url, 'POST', params=parameters)
        return [LedgerEntry._NewFromJsonDict(entry) for entry in resp['payload']]
    
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
        if verb == 'GET':
            url = self._build_url(url, params)
            try:
                resp = requests.get(url)
            except requests.RequestException as e:
                raise
        elif verb == 'POST':
            try:
                resp = requests.post(url, data=params)
            except requests.RequestException as e:
                raise
        if resp.status_code != 200:
            raise ApiError({u'message': 'Response Status Code: %d' % resp.status_code})
 
        data = self._parse_json(resp.content.decode('utf-8'))
        return data

    def _build_url(self, url, params):
        if params and len(params) > 0:
            url = url+'?'+self._encode_parameters(params)
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
        if 'success' in data:
            if data['success'] != True:
                raise ApiError(data['error'])
        if 'error' in data:
            raise ApiError(data['error'])
        if isinstance(data, (list, tuple)) and len(data)>0:
            if 'error' in data[0]:
                raise ApiError(data[0]['error'])
        

     
     

