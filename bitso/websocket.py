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

import json
import time
import thread

from ws4py.client.threadedclient import WebSocketClient
from ws4py.messaging import Message, PingControlMessage
from models import StreamUpdate


class Listener(object):
    def on_connect(self):
        pass

    def on_update(self, json_data):
        pass

    def on_close(self, **kwargs):
        pass
        

class Client(object):
    def __init__(self, listener):
        self.listener = listener
        self._ws_url = 'wss://ws.bitso.com'
        self.ws_client = WebSocketClient(self._ws_url)
        self.ws_client.opened = self.listener.on_connect
        self.ws_client.received_message = self._received
        self.ws_client.closed = self._closed
        self.channels = []

    def connect(self, channels):
        self.channels = channels
        self.ws_client.opened = self._opened
        self.ws_client.connect()
        self.ws_client.run_forever()

    def close(self):
        self.ws_client.close()
        
    def _opened(self):
        for channel in self.channels:
            self.ws_client.send(json.dumps({ 'action': 'subscribe', 'book': 'btc_mxn', 'type': channel }))
        thread.start_new_thread(self._ping_server, ())
        self.listener.on_connect()

    def _received(self, m):
        #print m.data
        val = json.loads(m.data)
        obj = StreamUpdate(val)
        self.listener.on_update(obj)
        
    def _closed(self, code, reason):
        self.listener.on_close(code, reason)
        
    def _ping_server(self):
        while True:
            #keep-alive
            self.ws_client.send(PingControlMessage(u'ping'))
            time.sleep(20)
