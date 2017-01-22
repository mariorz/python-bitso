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


import time
import sys
import os
#parent folder import hack
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bitso

from ordertree import OrderTree
import logging
from decimal import Decimal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


client = None

class LiveOrderBook(object):
    def __init__(self, rest_book):
        self.bids = OrderTree()
        self.asks = OrderTree()

        for bid in rest_book.bids:
            self.bids.insert_price(bid.price, bid.amount, bid.oid)
        for ask in rest_book.asks:
            self.asks.insert_price(ask.price, ask.amount, ask.oid)


class LiveBookListener(bitso.bitsows.Listener):
    def __init__(self):
        self.order_book = None
        self.sequence_number = 0
        self.queued_msgs = []
        
    def on_connect(self):
        logging.info('Websocket Connection Established')
        api = bitso.Api()
        rest_book = api.order_book('btc_mxn', aggregate=False)
        self.order_book = LiveOrderBook(rest_book)
        logging.info('Order Book Fetched. Best ask: %.4f, Best bid: %.4f, Spread: %.4f'
                     % (self.order_book.asks.min_price,
                        self.order_book.bids.max_price,
                        self.order_book.asks.min_price - self.order_book.bids.max_price))
        self.sequence_number = rest_book.sequence

        
    def on_update(self, data):
        if data.channel == 'diff-orders':
            if data.sequence_number == None:
                #if no sequence_number and channel is diff-orders,
                #then this is a "subscribed" message, ignore
                return
            if self.sequence_number == 0:
                #queue updates while rest orderbook has not been fetched
                self.queued_msgs.append(data)
                return
            else:
                #apply queued msgs
                for msg in self.queued_msgs:
                    if data.sequence_number > self.sequence_number:
                        self.merge_orders(msg.updates)
                        self.sequence_number = data.sequence_number
                self.queued_msgs = []
                 
            for obj in data.updates:
                logging.info('New Order. %s: %.4f @ %.4f = %.4f'
                             % (obj.side, obj.amount, obj.rate, obj.value))
            self.merge_orders(data.updates)
            logging.info('Best ask: %.4f, Best bid: %.4f, Spread: %.4f'
                             % (self.order_book.asks.min_price,
                                self.order_book.bids.max_price,
                                self.order_book.asks.min_price - self.order_book.bids.max_price))
            if self.sequence_number != data.sequence_number-1:
                logging.error("Sequence Number not consecutive: data.sequence:%s self.sequence:%s" % (data.sequence_number, self.sequence_number))
                self.reset_connection()
            self.sequence_number = data.sequence_number

        elif data.channel == 'trades':
            for obj in data.updates:
                logging.info('New Trade. %.4f @ %.4f = %.4f ' %
                                 (obj.amount, obj.rate, obj.value))
                                
    def on_close(self):
        logging.info("Connection Closed.")
        
    def merge_orders(self, orders):
        for order in orders:
            tree = self.order_book.bids if order.side == 'bid' else self.order_book.asks
            tree.insert_price(order.rate, order.amount, order.oid)

    def reset_connection(self):
        global client
        client.close()
        start_live_book()

        
def start_live_book():
    global client
    listener = LiveBookListener()
    client = bitso.bitsows.Client(listener)
    channels = ['diff-orders', 'trades']
    client.connect(channels)

            
if __name__ == '__main__':
    start_live_book()

