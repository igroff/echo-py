#! /usr/bin/env python
from email.message import Message
import BaseHTTPServer
import logging
import signal
import json
import sys
import os

BaseHTTPServer.MessageClass = Message

responseBuffer = []
responseBufferLength = os.environ.get('RESPONSE_BUFFER_LENGTH', 10)
keepRunning = True



class EchoHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # a method for handling our any requests given, simply echo's back
    # the content of the request including any headers as a json object
    def handle_request(self):
        if self.path == "/____show":
            response_body = json.dumps(responseBuffer)
        else:
            resp_data = dict(clientAddress=self.client_address[0],
                method=self.command,
                uri=self.path,
                httpVersion=self.request_version,
                requestHeaders={key:self.headers[key] for key in self.headers.keys()}
            )
            # check for a request body, and if we have it we'll need to know how long
            # it is to read it
            request_length = int(resp_data['requestHeaders'].get('content-length', 0))
            if request_length:
                resp_data['body'] = self.rfile.read(request_length)
            responseBuffer.append(resp_data)
            # if we have more entries than our 'limit' just remove the oldest
            if len(responseBuffer) > responseBufferLength:
                responseBuffer.pop(0)
            response_body = json.dumps(resp_data)
        # everything is always good
        self.send_response(200, '')
        # we'll be returning json
        self.send_header('content-type', 'application/json')
        # we're sending the json object as the body, so length of the json object
        self.send_header('content-length', len(response_body))
        # first we end our header section as per HTTP requirements (\n), then
        # we write out our reponse
        self.wfile.write("\n%s" % response_body)

    def __getattr__(self, name):
        # if a method starting with do_ is being called, we're handling a 
        # request, as defined by BaseHTTPRequestHandler
        if "do_" == name[0:3]:
            return self.handle_request

    def log_message(self, format, *args):
        # Do not log resource access
        return

server = BaseHTTPServer.HTTPServer(('', int(os.environ.get('PORT', 8080))), EchoHandler)
try:
    server.serve_forever()
except KeyboardInterrupt, e:
    print("Shutdown...")
