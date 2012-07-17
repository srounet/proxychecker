#!/usr/bin/env python

import SimpleHTTPServer
import BaseHTTPServer


class SimpleRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        for header, value in self.headers.items():
            self.send_header(header, value)
        self.end_headers()

    def do_QUIT(self):
        self.send_response(200)
        self.end_headers()
        self.server.stop = True


class SimpleTCPServer(BaseHTTPServer.HTTPServer):
    def __init__(self, server_address, request_handler):
        self.allow_reuse_address = True
        BaseHTTPServer.HTTPServer.__init__(self, server_address, request_handler)

    def serve_forever(self):
        self.stop = False
        while not self.stop:
            self.handle_request()

def simple_http_server(host='0.0.0.0', port=29351):
    server_address = (host, port)
    httpd = SimpleTCPServer(server_address, SimpleRequestHandler)
    httpd.serve_forever()
