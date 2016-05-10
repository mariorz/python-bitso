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


from bintrees import FastRBTree

class OrderTree(object):
    def __init__(self):
        self.price_tree = FastRBTree()
        self.price_map = {} 
        self.min_price = None
        self.max_price = None


    def insert_price(self, price, amount):
        self.price_tree.insert(price, amount)
        self.price_map[price] = amount
        if self.max_price == None or price > self.max_price:
            self.max_price = price
        if self.min_price == None or price < self.min_price:
            self.min_price = price


    def update_price(self, price, amount):
        
        self.price_tree.insert(price, amount) #updates if key exists
        self.price_map[price] = amount
        
    def remove_price(self, price):
        self.price_tree.remove(price)
        del self.price_map[price]

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

    def price_exists(self, price):
        return price in self.price_map

    def max(self):
        return self.max_price

    def min(self):
        return self.min_price
