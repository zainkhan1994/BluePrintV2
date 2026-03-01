#!/usr/bin/env python3
"""Simple CORS proxy that forwards requests to localhost:8100 and adds CORS headers.
Usage: python3 tools/cors_proxy.py [port]
"""
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import request, parse

BACKEND_ORIGIN = ('127.0.0.1', 8100)


class ProxyHandler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors_headers()
        self.end_headers()

    def _forward(self):
        # Build target URL on backend using same path+query
        target = f'http://{BACKEND_ORIGIN[0]}:{BACKEND_ORIGIN[1]}' + self.path
        data = None
        if 'Content-Length' in self.headers:
            length = int(self.headers['Content-Length'])
            data = self.rfile.read(length)

        req = request.Request(target, data=data, method=self.command)
        # copy select headers
        for k in self.headers:
            if k.lower() in ('host', 'content-length', 'accept-encoding', 'connection'):
                continue
            req.add_header(k, self.headers[k])

        try:
            with request.urlopen(req, timeout=20) as resp:
                self.send_response(resp.getcode())
                # forward headers
                for key, val in resp.getheaders():
                    # skip hop-by-hop headers
                    if key.lower() in ('transfer-encoding', 'connection', 'keep-alive'):
                        continue
                    self.send_header(key, val)
                # add CORS
                self._set_cors_headers()
                self.end_headers()
                body = resp.read()
                if body:
                    self.wfile.write(body)
        except Exception as exc:
            self.send_response(502)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(str(exc).encode('utf-8'))

    def do_GET(self):
        self._forward()

    def do_POST(self):
        self._forward()

    def do_PUT(self):
        self._forward()

    def do_DELETE(self):
        self._forward()


def run(port: int = 8086):
    server = HTTPServer(('127.0.0.1', port), ProxyHandler)
    print(f'CORS proxy listening on http://127.0.0.1:{port} forwarding to http://{BACKEND_ORIGIN[0]}:{BACKEND_ORIGIN[1]}')
    server.serve_forever()


if __name__ == '__main__':
    port = 8086
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except Exception:
            pass
    run(port)
