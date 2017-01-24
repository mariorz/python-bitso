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

import sys
from bintrees import FastRBTree
import logging
from decimal import Decimal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class OrderTree(object):
    def __init__(self):
        self.price_tree = FastRBTree()
        self.min_price = None
        self.max_price = None

    def get_orders_at_price(self, price):
        return self.price_tree.get(price)

        
    def insert_price(self, price, amount, oid):
        ## ignore market order
        if price == Decimal(0.0):            
            return
        prev_val = self.get_orders_at_price(price)
        if prev_val != None:
            ## price exists in local order book
            if oid in prev_val:
                ## update to an existing order at price
                prev_val['total'] = prev_val['total'] - prev_val[oid] + amount
                prev_val[oid] = amount
            else:
                ## new order at price
                prev_val['total'] += amount
                prev_val[oid] = amount
            self.price_tree.insert(price, prev_val)
        elif amount != 0.0:
            ## price did not exit in order book
            val = {'total': amount, oid: amount}
            self.price_tree.insert(price, val)

        try:
            val = self.price_tree.get(price)
            if val['total'] > 0:
                if self.max_price == None or price > self.max_price:
                    self.max_price = price
                if self.min_price == None or price < self.min_price:
                    self.min_price = price
            elif val['total'] == 0:
                ## price removed from orderbook
                self.remove_price(price)
            else:
                ## something has gone terribly wrong
                logging.error("total amount at price %s went to negative amounts" % (price))

        except:
            logging.error("price (%s) does not exist in orderbook" % (price))
        
    def remove_price(self, price):
        self.price_tree.remove(price)
        if self.max_price == price:
            try:
                self.max_price = max(self.price_tree)
            except ValueError:
                self.max_price = None
        if self.min_price == price:
            try:
                self.min_price = min(self.price_tree)
            except ValueError:
                self.min_price = None

