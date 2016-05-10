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

#parent folder import hack
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bitso

from ordertree import OrderTree
import logging
from decimal import Decimal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



class LiveOrderBook(object):
    def __init__(self, init_book):
        self.init_book = init_book
        self.bids = OrderTree()
        self.asks = OrderTree()

        for bid in self.init_book.bids:
            self.bids.insert_price(bid['price'], bid['amount'])
        for ask in self.init_book.asks:
            self.asks.insert_price(ask['price'], ask['amount'])


class LiveBookListener(bitso.websocket.Listener):
    def __init__(self, order_book):
        self.order_book = order_book
        
    def on_connect(self):
        logging.info('Websocket Connection Established')
        
    def on_update(self, data):
        if data.channel == 'diff-orders':
            for obj in data.updates:
                logging.info('New Order. %s: %.4f @ %.4f = %.4f'
                             % (obj.side, obj.amount, obj.rate, obj.value))
            self.merge_orders(data.updates)
            logging.info('Best ask: %.4f, Best bid: %.4f, Spread: %.4f'
                             % (order_book.asks.min(),
                                order_book.bids.max(),
                                order_book.asks.min()-order_book.bids.max()))
        elif data.channel == 'trades':
            for obj in data.updates:
                logging.info('New Trade. %.4f @ %.4f = %.4f ' %
                                 (obj.amount, obj.rate, obj.value))
                
            

    def on_close(self, code, reason=None):
        logging.info("Connection Closed. code:%s, reason:%s" % (str(code), reason))


    def merge_orders(self, orders):
        for order in orders:
            tree = self.order_book.bids if order.side == 'bid' else self.order_book.asks
            if order.amount == Decimal(0.0):
                try:
                    tree.remove_price(order.rate)
                    logging.info("Removed price level at: %.4f" % (order.rate))
                except KeyError:
                    logging.warning("Tried to remove price that does not exist in tree: %.4f"
                                    % (order.rate))
            else:
                if tree.price_exists(order.rate):
                    tree.update_price(order.rate, order.amount)
                else:
                    tree.insert_price(order.rate, order.amount)

if __name__ == '__main__':
    try:
        api = bitso.Api()
        order_book = LiveOrderBook(api.order_book())
        logging.info('Order Book Fetched. Best ask: %.4f, Best bid: %.4f, Spread: %.4f'
                     % (order_book.asks.min(),
                        order_book.bids.max(),
                        order_book.asks.min()-order_book.bids.max()))
        listener = LiveBookListener(order_book)
        client = bitso.websocket.Client(listener)
        channels = ['trades', 'diff-orders']
        client.connect(channels)
    except KeyboardInterrupt:
        client.close()
