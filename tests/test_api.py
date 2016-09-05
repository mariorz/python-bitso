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

import mock
import os
import unittest
import sys
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bitso

from decimal import Decimal

class FakeResponse(requests.Response):
    def __init__(self, content='', status_code=200):
        super(FakeResponse, self).__init__()
        self._content = content
        self._content_consumed = True
        self.status_code = status_code

class PublicApiTest(unittest.TestCase):
    def setUp(self):
        self.api = bitso.Api()

    def test_bad_response(self):
        response = FakeResponse(b'''{"error": "something went wrong"}''')
        with mock.patch('requests.get', return_value=response):
            self.assertRaises(
                bitso.ApiError, self.api.ticker)

    def test_404_response(self):
        response = FakeResponse(status_code=404)
        with mock.patch('requests.get', return_value=response):
            self.assertRaises(bitso.ApiError, self.api.ticker)

    def test_500_response(self):
        response = FakeResponse(status_code=500)
        with mock.patch('requests.get', return_value=response):
            self.assertRaises(bitso.ApiError, self.api.ticker)

    def test_ticker(self):
        response = FakeResponse(b'''
            {"volume": "22.31349615",
            "high": "5750.00",
            "last": "5633.98",
            "low": "5450.00",
            "vwap": "5393.45",
            "ask": "5632.24",
            "bid": "5520.01",
            "timestamp": "1447348096"
        }''')
        with mock.patch('requests.get', return_value=response):
            ticker = self.api.ticker('btc_mxn')
        self.assertIsInstance(ticker, bitso.Ticker)



    def test_order_book_ungrouped(self):
        with open('tests/order_book_ungrouped.json') as data_file:   
            response = FakeResponse(data_file.read().replace('\n', ''))
        with mock.patch('requests.get', return_value=response):
            result = self.api.order_book(group=False)
        self.assertIsInstance(result, bitso.OrderBook)
        self.assertIsInstance(result.asks, list)
        self.assertEqual(len(result.asks), 399)
        self.assertIsInstance(result.bids, list)
        self.assertEqual(len(result.bids), 318)
        self.assertEqual(result.asks[0]['price'], Decimal("10859.05"))
        self.assertEqual(result.asks[0]['amount'], Decimal("2.55631938"))
        self.assertEqual(result.bids[0]['price'], Decimal("10810.80"))
        self.assertEqual(result.bids[0]['amount'], Decimal("0.00138759"))

        
                            
    def test_order_book_grouped(self):
        response = FakeResponse(b'''
            {"asks": [
               ["5632.24", "1.34491802"],
               ["5632.25", "1.00000000"],
               ["5633.99", "0.61980799"]
            ],
            "bids": [
               ["5520.01", "0.34493053"],
               ["5520.00", "0.08000000"],
               ["5486.01", "0.00250000"]
            ],
            "timestamp": "1447348416"}''')
        with mock.patch('requests.get', return_value=response):
            result = self.api.order_book(group=True)
        self.assertIsInstance(result, bitso.OrderBook)
        self.assertIsInstance(result.asks, list)
        self.assertEqual(len(result.asks), 3)
        self.assertIsInstance(result.bids, list)
        self.assertEqual(len(result.bids), 3)
        self.assertEqual(result.asks[0]['price'], Decimal("5632.24"))
        self.assertEqual(result.asks[0]['amount'], Decimal("1.34491802"))
        self.assertEqual(result.bids[0]['price'], Decimal("5520.01"))
        self.assertEqual(result.bids[0]['amount'], Decimal("0.34493053"))


        
    def test_transactions(self):
        response = FakeResponse(b'''
        [
           {
               "date": "1447350465",
               "amount": "0.02000000",
               "side": "buy",
               "price": "5545.01",
               "tid": 55845
            },
            {
               "date": "1447347533",
               "amount": "0.33723939",
               "side": "sell",
               "price": "5633.98",
               "tid": 55844
            }
        ]''')
        with mock.patch('requests.get', return_value=response):
            txs = self.api.transactions(book='btc_mxn', time='hour')
        self.assertIsInstance(txs, list)
        self.assertEqual(len(txs), 2)
        self.assertEqual(txs[0].price, Decimal("5545.01"))
        self.assertEqual(txs[0].timestamp, "1447350465")


          
    def test_transactions_time_fail(self):
        self.assertRaises(bitso.ApiClientError,
                          self.api.transactions, 'btc_mxn', 'hours')


    

                

class PrivateApiTest(unittest.TestCase):
    def setUp(self):
        self.api = bitso.Api('id', 'key','secret')


    def test_account_balance(self):
        response = FakeResponse(b'''
        {"btc_available": "46.67902107",
         "fee": "1.0000",
         "mxn_available": "26864.57",
         "btc_balance": "46.67902107",
         "mxn_reserved": "0.00",
         "mxn_balance": "26864.57",
         "btc_reserved": "0.00000000"}''')
        with mock.patch('requests.post', return_value=response):
            result = self.api.balance()
        print result
        self.assertIsInstance(result, bitso.Balance)
        self.assertEqual(result.btc_available, Decimal("46.67902107"))
        self.assertEqual(result.mxn_available, Decimal("26864.57"))
        self.assertEqual(result.fee, Decimal("1.0"))
    

    def test_user_transactions(self):
        response = FakeResponse(b'''
        [
           {
              "datetime": "2015-10-10 16:19:33",
              "method": "Bitcoin",
              "btc": "0.48650929",
              "type": 0
            },
            {
              "datetime": "2015-10-09 13:49:00",
              "method": "SPEI Transfer",
              "mxn": "-1800.15",
              "type": 1
            },
            {
              "btc": "-0.25232073",
              "datetime": "2015-10-09 13:45:46",
              "mxn": "1023.77",
              "rate": "4057.45",
              "id": 51756,
              "type": 2,
              "order_id": "19vaqiv72drbphig81d3y1ywri0yg8miihs80ng217drpw7xyl0wmytdhtby2ygk"
            }
        ] ''')
        with mock.patch('requests.post', return_value=response):
            txs = self.api.user_transactions(sort='desc')
        print txs
        self.assertIsInstance(txs, list)
        self.assertEqual(len(txs), 3)
        self.assertEqual(txs[0].btc, Decimal("0.48650929"))
        self.assertEqual(txs[0].type, 'deposit')
        self.assertEqual(txs[1].mxn, Decimal("-1800.15"))
        self.assertEqual(txs[1].method, "SPEI Transfer")
        self.assertEqual(txs[1].type, 'withdrawal')
        self.assertEqual(txs[2].rate, Decimal("4057.45"))
        self.assertEqual(txs[2].type, 'trade')
        self.assertEqual(txs[2].order_id,
                        "19vaqiv72drbphig81d3y1ywri0yg8miihs80ng217drpw7xyl0wmytdhtby2ygk")


    
    def test_user_transactions_fail(self):
        self.assertRaises(bitso.ApiClientError,
                          self.api.user_transactions, sort='dec')


    

        
    def test_open_orders(self):
        response = FakeResponse(b'''
        [
           {
              "amount": "0.01000000",
              "datetime": "2015-11-12 12:37:01",
              "price": "5600.00",
              "id": "543cr2v32a1h684430tvcqx1b0vkr93wd694957cg8umhyrlzkgbaedmf976ia3v",
              "type": "1",
              "status": "1"
           },
           {
              "amount": "0.12680000",
              "datetime": "2015-11-12 12:33:47",
              "price": "4000.00",
              "id": "qlbga6b600n3xta7actori10z19acfb20njbtuhtu5xry7z8jswbaycazlkc0wf1",
              "type": "0",
              "status": "0"
           },
           {
              "amount": "1.12560000",
              "datetime": "2015-11-12 12:33:23",
              "price": "6123.55",
              "id": "d71e3xy2lowndkfmde6bwkdsvw62my6058e95cbr08eesu0687i5swyot4rf2yf8",
              "type": "1",
              "status": "0"
            }
        ] ''')
        with mock.patch('requests.post', return_value=response):
            result = self.api.open_orders()
        print result
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].amount, Decimal("0.01000000"))
        self.assertEqual(result[0].type, 'sell')
        self.assertEqual(result[0].status, 'partial')
        self.assertEqual(result[1].type, 'buy')
        self.assertEqual(result[1].status, 'active')
        self.assertEqual(result[1].price, Decimal("4000"))
        self.assertEqual(result[2].type, 'sell')
        self.assertEqual(result[2].status, 'active')
        self.assertEqual(result[2].price, Decimal("6123.55"))


    def test_lookup_order(self):
        response = FakeResponse(b'''
        [{"status": "0", "created": "2016-08-30 18:05:12", "price": "15801.23", "amount": "0.01000000", "book": "btc_mxn", "type": "1", "id": "X45g3MhXJpVcpl7VsM25l5Mkv7nhJO5rOvf8lnqnso9nOOXir7vrR5mcld587sMo"}]''')
        with mock.patch('requests.post', return_value=response):
            result = self.api.lookup_order('X45g3MhXJpVcpl7VsM25l5Mkv7nhJO5rOvf7lnqnso9nOOXir7vrR5mcld587sMo')

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].type, 'sell')
        self.assertEqual(result[0].price, Decimal('15801.23'))
        self.assertEqual(result[0].amount, Decimal('0.01000000'))
    
    def test_cancel_order(self):
        response = FakeResponse(b'''"true"''')
        with mock.patch('requests.post', return_value=response):
            result = self.api.cancel_order('X45g3MhXJpVcpl7VsM25l5Mkv7nhJO5rOvf7lnqnso9nOOXir7vrR5mcld587sMo')
        self.assertEqual(result, 'true')

    def test_btc_deposit_address(self):
        response = FakeResponse(b'''"3Kejck1J6aKSMZs3fSfbpb5szieJ6RA9rj"''')
        with mock.patch('requests.post', return_value=response):
            result = self.api.btc_deposit_address()
        self.assertEqual(result, '3Kejck1J6aKSMZs3fSfbpb5szieJ6RA9rj')


    def test_btc_withdrawal(self):
        response = FakeResponse(b'''"ok"''')
        with mock.patch('requests.post', return_value=response):
            result = self.api.btc_withdrawal('.01','1Hnv5fFaWUTChfBHPizfeNjGvi1ep7tCkt')
        self.assertEqual(result, 'ok')
        
    
    def test_lookup_orders(self):
        response = FakeResponse(b'''[{
           "amount": "0.01000000",
           "created": "2015-11-12 12:37:01",
           "price": "5600.00",
           "book": "btc_mxn",
           "id": "543cr2v32a1h684430tvcqx1b0vkr93wd694957cg8umhyrlzkgbaedmf976ia3v",
           "type": "1",
           "updated": "2015-11-12 12:37:40",
           "status": "-1"
        }]''')
        with mock.patch('requests.post', return_value=response):
            result = self.api.open_orders()
        print result
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].amount, Decimal("0.01000000"))
        self.assertEqual(result[0].price, Decimal("5600"))
        self.assertEqual(result[0].type, 'sell')
        self.assertEqual(result[0].status, 'cancelled')
        

    def test_buy_limit_order(self):
        response = FakeResponse(b'''
           {
              "amount": "0.10000000",
              "datetime": "2015-11-12 12:53:28",
              "price": "100.00",
              "book": "btc_mxn",
              "id": "kidxgibf009w85qykad1sdoktdmdlbo6t23akepkfzgn56mphzracfv6thjfs8lm",
              "type": "0",
              "status": "0"
            }''')
        with mock.patch('requests.post', return_value=response):
            result = self.api.buy(amount='0.1', price='100')
        self.assertIsInstance(result, bitso.Order)

    def test_sell_limit_order(self):
        response = FakeResponse(b'''
           {
              "amount": "0.01000000",
              "datetime": "2015-11-12 13:29:33",
              "price": "10000.00",
              "book": "btc_mxn",
              "id": "5umhs73uxry9ykblk923xxi48j4jhcwm7i40q7vnztxxd8jyil1gjkkr4obl1789",
              "type": "1",
              "status": "0"
            }''')
        with mock.patch('requests.post', return_value=response):
            result = self.api.sell('.01', '10000')
        print result
        self.assertIsInstance(result, bitso.Order)
        


    def test_transfer_quote(self):
        response = FakeResponse(b'''
        {
           "quote":{
              "btc_amount":"0.14965623",
              "currency":"MXN",
              "rate":"3340.99",
              "gross":"500.00",
              "outlets":{
                 "sp":{
                    "id":"sp",
                    "name":"SPEI Transfer",
                    "required_fields":[
                       "recipient_given_names",
                       "recipient_family_names",
                       "clabe",
                       "bank_name"
                    ],
                    "minimum_transaction":"500.00",
                    "maximum_transaction":"2500000.00",
                    "daily_limit":"10000.00",
                    "fee":"12.00",
                    "net":"488.00",
                    "available":"1",
                    "verification_level_requirement":"0"
                 },
                 "vo":{
                    "id":"vo",
                    "name":"Voucher",
                    "required_fields":[
                       "email_address"
                    ],
                    "minimum_transaction":"25.00",
                    "maximum_transaction":"9999.00",
                    "fee":"0.00",
                    "daily_limit":"0.00",
                    "net":"500.00",
                    "available":"1",
                    "verification_level_requirement":"0"
                 },
                 "rp":{
                    "id":"rp",
                    "name":"Ripple",
                    "required_fields":[
                       "ripple_address"
                    ],
                    "minimum_transaction":"0.00",
                    "maximum_transaction":"10000000.00",
                    "fee":"5.00",
                    "daily_limit":"0.00",
                    "net":"495.00",
                    "available":"1",
                "verification_level_requirement":"0"
             },
             "pm":{
                "id":"pm",
                "name":"Pademobile",
                "required_fields":[
                   "phone_number"
                ],
                "minimum_transaction":"1.00",
                "maximum_transaction":"1000000.00",
                "fee":"0.00",
                "daily_limit":"0.00",
                "net":"500.00",
                "available":"1",
                "verification_level_requirement":"0"
             },
             "bw":{
                "id":"bw",
                "name":"Bank Wire",
                "required_fields":[
                   "recipient_full_name",
                   "account_holder_address",
                   "bank_name",
                   "bank_address",
                   "account_number",
                   "swift",
                   "other_instructions"
                ],
                "minimum_transaction":"1000.00",
                "maximum_transaction":"2500000.00",
                "daily_limit":"2500000.00",
                "fee":"500.00",
                "net":"0.00",
                "available":"1",
                "verification_level_requirement":"0"
             }
          },
          "timestamp":"1425101044",
          "expires_epoch":"1425101104"
       },
       "success":true
        }''')
        with mock.patch('requests.post', return_value=response):
            result = self.api.transfer_quote(amount='0.14965623', currency='MXN')
        print result
        self.assertIsInstance(result, bitso.TransactionQuote)
        self.assertEqual(result.success, True)
        self.assertEqual(result.btc_amount, Decimal('0.14965623'))
        self.assertEqual(result.currency, 'MXN')
        self.assertEqual(result.rate, Decimal('3340.99'))
        self.assertEqual(result.gross, Decimal('500.00'))
        self.assertIsInstance(result.outlets, dict)
        self.assertEqual(result.outlets['sp']['minimum_transaction'], Decimal('500.00'))
        self.assertEqual(result.outlets['sp']['maximum_transaction'], Decimal('2500000.00'))
        self.assertEqual(result.outlets['bw']['daily_limit'], Decimal('2500000.00'))
        self.assertEqual(result.outlets['bw']['fee'], Decimal('500.00'))
        self.assertEqual(result.outlets['bw']['net'], Decimal('0.00'))
        self.assertEqual(result.outlets['bw']['available'], True)


    def test_create_transfer(self):
        response = FakeResponse(b'''
        {
            "order":{
              "btc_amount":"0.14965623",
              "btc_pending":"0",
              "btc_received":"0",
              "confirmation_code":"9b2a4",
              "created_at":"1425101044",
              "currency":"MXN",
              "currency_amount":"0",
              "currency_fees":"0",
              "currency_settled":"0",
              "expires_epoch":1425101104,
              "fields":{
                 "phone_number":"5554181042"
              },
              "id":"9b2a431b98597312e99cbff1ba432cbf",
              "payment_outlet_id":"pm",
              "qr_img_uri":"https:\/\/chart.googleapis.com\/chart?chl=bitcoin%3AmgKZfNdFJgztvfvhEaGgMTQRQ2iHCadHGa%3Famount%3D0.14965623&chs=400x400&cht=qr&choe=UTF-8&chld=L%7C0",
              "user_uri":"https:\/\/api.bitso.com\/v2\/transfer\/9b2a431b98597312e99cbff1ba432cbf",
              "wallet_address":"mgKZfNdFJgztvfvhEaGgMTQRQ2iHCadHGa"
           },
           "success":true
        }''')
        with mock.patch('requests.post', return_value=response):
            result = self.api.transfer_create(btc_amount='0.14965623',
                                   currency='MXN',
                                   rate='7585.20',
                                   payment_outlet='pm')
        print result
        self.assertIsInstance(result, bitso.TransactionOrder)
        self.assertEqual(result.success, True)
        self.assertEqual(result.btc_amount, Decimal('0.14965623'))

        self.assertEqual(result.btc_pending, Decimal('0'))
        self.assertEqual(result.btc_received, Decimal('0.0'))
        self.assertEqual(result.confirmation_code, '9b2a4')
        self.assertEqual(result.currency, 'MXN')
        self.assertEqual(result.fields['phone_number'], '5554181042')
        self.assertEqual(result.btc_amount, Decimal('0.14965623'))
        self.assertEqual(result.wallet_address, 'mgKZfNdFJgztvfvhEaGgMTQRQ2iHCadHGa')
        

    def test_ledger(self):
        with open('tests/ledger.json') as data_file:   
            response = FakeResponse(data_file.read().replace('\n', ''))
        with mock.patch('requests.post', return_value=response):
            result = self.api.ledger()
        for item in result:
            for bu in item.balance_updates:
                self.assertIsInstance(bu, bitso.BalanceUpdate)
                self.assertIsInstance(bu.amount, Decimal)

        
        
if __name__ == '__main__':
    unittest.main()
