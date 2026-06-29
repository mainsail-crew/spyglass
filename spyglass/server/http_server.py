from __future__ import annotations

import asyncio
import socketserver
from collections.abc import Callable, Coroutine
from http import HTTPStatus, server
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from spyglass.camera.lazy_encoder import LazyEncoder

from picamera2 import Picamera2

from spyglass import WEBRTC_ENABLED
from spyglass.server import controls, jpeg, webrtc_whep
from spyglass.url_parsing import check_urls_match


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class StreamingHandler(server.BaseHTTPRequestHandler):
    loop = asyncio.new_event_loop()
    mjpeg_encoder: LazyEncoder
    h264_encoder: LazyEncoder | None
    picam2: Picamera2
    stream_url: str
    snapshot_url: str
    webrtc_url: str
    media_track: webrtc_whep.PicameraStreamTrack
    exif_header: bytes | None

    def get_frame(self, /) -> bytes: ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        if self.check_url(self.stream_url) or self.check_url("/stream"):
            jpeg.start_streaming(self)
        elif self.check_url(self.snapshot_url) or self.check_url("/snapshot"):
            jpeg.send_snapshot(self)
        elif self.check_url("/controls"):
            controls.do_GET(self)
        elif self.check_webrtc():
            pass
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_OPTIONS(self) -> None:
        if self.check_webrtc():
            webrtc_whep.do_OPTIONS(self, self.webrtc_url)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.check_webrtc():
            self.run_async_request(webrtc_whep.do_POST_async)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_PATCH(self) -> None:
        if self.check_webrtc():
            self.run_async_request(webrtc_whep.do_PATCH_async)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def check_url(self, url: str, match_full_path: bool = True) -> bool:
        return check_urls_match(url, self.path, match_full_path)

    def check_webrtc(self) -> bool:
        return WEBRTC_ENABLED and (
            self.check_url(self.webrtc_url, match_full_path=False)
            or self.check_url("/webrtc", match_full_path=False)
        )

    def run_async_request(
        self,
        method: Callable[["StreamingHandler"], Coroutine[Any, Any, None]],
    ) -> None:
        asyncio.run_coroutine_threadsafe(method(self), StreamingHandler.loop).result()
