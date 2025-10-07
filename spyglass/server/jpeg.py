from http import HTTPStatus

# Used for type hinting
from typing import TYPE_CHECKING

from spyglass import logger

if TYPE_CHECKING:
    from spyglass.server.http_server import StreamingHandler


def start_streaming(handler: "StreamingHandler"):
    try:
        send_default_headers(handler)
        handler.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
        handler.end_headers()
        while True:
            frame = handler.get_frame()
            handler.wfile.write(b"--FRAME\r\n")
            if handler.exif_header is None:
                send_jpeg_content_headers(handler, frame)
                handler.wfile.write(frame)
                handler.wfile.write(b"\r\n")
            else:
                send_jpeg_content_headers(handler, frame, len(handler.exif_header) - 2)
                handler.wfile.write(handler.exif_header)
                handler.wfile.write(frame[2:])
                handler.wfile.write(b"\r\n")
    except Exception as e:
        logger.warning(
            "Removed streaming client %s: %s", handler.client_address, str(e)
        )


def send_snapshot(handler: "StreamingHandler"):
    try:
        send_default_headers(handler)
        frame = handler.get_frame()
        if handler.exif_header is None:
            send_jpeg_content_headers(handler, frame)
            handler.wfile.write(frame)
        else:
            send_jpeg_content_headers(handler, frame, len(handler.exif_header) - 2)
            handler.wfile.write(handler.exif_header)
            handler.wfile.write(frame[2:])
    except Exception as e:
        logger.warning("Removed client %s: %s", handler.client_address, str(e))


def send_default_headers(handler: "StreamingHandler"):
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Age", 0)
    handler.send_header("Cache-Control", "no-cache, private")
    handler.send_header("Pragma", "no-cache")


def send_jpeg_content_headers(handler: "StreamingHandler", frame, extra_len=0):
    handler.send_header("Content-Type", "image/jpeg")
    handler.send_header("Content-Length", str(len(frame) + extra_len))
    handler.end_headers()
