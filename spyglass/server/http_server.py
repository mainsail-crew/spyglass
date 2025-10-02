#!/usr/bin/python3

import asyncio
import socketserver
from http import HTTPStatus, server

from spyglass import WEBRTC_ENABLED
from spyglass.server import controls, jpeg, webrtc_whep
from spyglass.url_parsing import check_urls_match


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class StreamingHandler(server.BaseHTTPRequestHandler):
    loop = asyncio.new_event_loop()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.check_url(self.stream_url):
            jpeg.start_streaming(self)
        elif self.check_url(self.snapshot_url):
            jpeg.send_snapshot(self)
        elif self.check_url("/controls"):
            controls.do_GET(self)
        elif self.check_webrtc():
            pass
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_OPTIONS(self):
        if self.check_webrtc():
            webrtc_whep.do_OPTIONS(self, self.webrtc_url)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self):
        if self.check_webrtc():
            self.run_async_request(webrtc_whep.do_POST_async)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_PATCH(self):
        if self.check_webrtc():
            self.run_async_request(webrtc_whep.do_PATCH_async)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def check_url(self, url, match_full_path=True):
        return check_urls_match(url, self.path, match_full_path)

    def check_webrtc(self):
        return WEBRTC_ENABLED and self.check_url(self.webrtc_url, match_full_path=False)

    def run_async_request(self, method):
        asyncio.run_coroutine_threadsafe(method(self), StreamingHandler.loop).result()
