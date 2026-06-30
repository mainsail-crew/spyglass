from __future__ import annotations

import asyncio
import uuid
from collections import deque
from fractions import Fraction
from http import HTTPStatus
from typing import TYPE_CHECKING

from picamera2.outputs import Output

from spyglass import WEBRTC_ENABLED
from spyglass.camera.lazy_encoder import LazyEncoder
from spyglass.url_parsing import check_urls_match

if TYPE_CHECKING:
    from aiortc import (
        MediaStreamTrack,
        RTCPeerConnection,
        RTCRtpCodecCapability,
        RTCRtpTransceiver,
        RTCSessionDescription,
        sdp,
    )
    from aiortc.contrib.media import MediaRelay
    from aiortc.rtcicetransport import RTCIceCandidate
    from aiortc.rtcrtpsender import RTCRtpSender
    from av.packet import Packet

    from spyglass.server.http_server import StreamingHandler
else:
    if WEBRTC_ENABLED:
        from aiortc import MediaStreamTrack
        from av.packet import Packet
    else:

        class MediaStreamTrack:
            pass


# Module-level variables populated at runtime when WEBRTC_ENABLED is True.
pcs: dict[str, RTCPeerConnection] = {}
max_connections: int = 20
media_relay: MediaRelay

if WEBRTC_ENABLED:
    from aiortc import RTCPeerConnection, RTCSessionDescription, sdp
    from aiortc.contrib.media import MediaRelay
    from aiortc.rtcrtpsender import RTCRtpSender

    max_connections = 20
    media_relay = MediaRelay()


def send_default_headers(response_code: int, handler: StreamingHandler) -> None:
    handler.send_response(response_code)
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Credentials", "false")


def do_OPTIONS(handler: StreamingHandler, webrtc_url: str = "/webrtc") -> None:
    # Adapted from MediaMTX http_server.go
    # https://github.com/bluenviron/mediamtx/blob/main/internal/servers/webrtc/http_server.go#L173-L189
    def response_headers() -> None:
        send_default_headers(HTTPStatus.NO_CONTENT, handler)
        handler.send_header(
            "Access-Control-Allow-Methods", "OPTIONS, GET, POST, PATCH, DELETE"
        )
        handler.send_header(
            "Access-Control-Allow-Headers", "Authorization, Content-Type, If-Match"
        )

    if handler.headers.get("Access-Control-Request-Method") is not None:
        response_headers()
        handler.end_headers()
    elif check_urls_match(f"{webrtc_url}/whip", handler.path) or check_urls_match(
        f"{webrtc_url}/whep", handler.path
    ):
        response_headers()
        handler.send_header("Access-Control-Expose-Headers", "Link")
        ice_servers = get_ICE_servers()
        if ice_servers is not None:
            handler.headers["Link"] = ice_servers
        handler.end_headers()


async def do_POST_async(handler: StreamingHandler) -> None:
    # Adapted from MediaMTX http_server.go
    # https://github.com/bluenviron/mediamtx/blob/main/internal/servers/webrtc/http_server.go#L191-L246
    if handler.headers.get("Content-Type") != "application/sdp":
        handler.send_error(HTTPStatus.BAD_REQUEST)
        return

    # Limit simultanous clients to save resources
    if len(pcs) >= max_connections:
        handler.send_error(
            HTTPStatus.TOO_MANY_REQUESTS, message="Too many clients connected"
        )
        return

    content_length = int(handler.headers["Content-Length"])
    offer_text = handler.rfile.read(content_length).decode("utf-8")
    offer: RTCSessionDescription = RTCSessionDescription(sdp=offer_text, type="offer")

    pc: RTCPeerConnection = RTCPeerConnection()
    secret = uuid.uuid4()

    h264_encoder: LazyEncoder | None = getattr(handler, "h264_encoder", None)
    encoder_acquired = False

    def _cleanup() -> None:
        nonlocal encoder_acquired
        pcs.pop(str(secret), None)
        if h264_encoder is not None and encoder_acquired:
            encoder_acquired = False
            h264_encoder.release()

    @pc.on("connectionstatechange")
    async def on_connectionstatechange() -> None:
        print(f"Connection state {pc.connectionState}")
        if pc.connectionState == "failed":
            await pc.close()
        elif pc.connectionState == "closed":
            _cleanup()
            print(f"{len(pcs)} connections still open.")

    try:
        if h264_encoder is not None:
            h264_encoder.acquire()
            encoder_acquired = True

        pcs[str(secret)] = pc

        track: MediaStreamTrack = media_relay.subscribe(handler.media_track)
        sender: RTCRtpSender = pc.addTrack(track)
        codecs: list[RTCRtpCodecCapability] = RTCRtpSender.getCapabilities(
            "video"
        ).codecs
        transceiver: RTCRtpTransceiver = next(
            t for t in pc.getTransceivers() if t.sender == sender
        )
        transceiver.setCodecPreferences(
            [codec for codec in codecs if codec.mimeType == "video/H264"]
        )

        await pc.setRemoteDescription(offer)
        answer: RTCSessionDescription = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        while pc.iceGatheringState != "complete":
            await asyncio.sleep(1)

        send_default_headers(HTTPStatus.CREATED, handler)

        handler.send_header("Content-Type", "application/sdp")
        handler.send_header("ETag", "*")

        handler.send_header("ID", str(secret))
        handler.send_header(
            "Access-Control-Expose-Headers", "ETag, ID, Accept-Patch, Link, Location"
        )
        handler.send_header("Accept-Patch", "application/trickle-ice-sdpfrag")
        ice_servers = get_ICE_servers()
        if ice_servers is not None:
            handler.headers["Link"] = ice_servers
        handler.send_header("Location", f"/whep/{secret}")
        handler.send_header("Content-Length", str(len(pc.localDescription.sdp)))
        handler.end_headers()
        handler.wfile.write(bytes(pc.localDescription.sdp, "utf-8"))
    except Exception:
        _cleanup()
        await pc.close()
        raise


async def do_PATCH_async(streaming_handler: StreamingHandler) -> None:
    # Adapted from MediaMTX http_server.go
    # https://github.com/bluenviron/mediamtx/blob/main/internal/servers/webrtc/http_server.go#L248-L287
    if (
        len(streaming_handler.path.split("/")) < 3
        or streaming_handler.headers.get("Content-Type")
        != "application/trickle-ice-sdpfrag"
    ):
        send_default_headers(HTTPStatus.BAD_REQUEST, streaming_handler)
        streaming_handler.end_headers()
        return
    content_length = int(streaming_handler.headers["Content-Length"])
    sdp_str = streaming_handler.rfile.read(content_length).decode("utf-8")
    candidates: list[RTCIceCandidate] = parse_ice_candidates(sdp_str)
    secret = streaming_handler.path.split("/")[-1]
    pc: RTCPeerConnection = pcs[secret]
    for candidate in candidates:
        await pc.addIceCandidate(candidate)

    send_default_headers(HTTPStatus.NO_CONTENT, streaming_handler)
    streaming_handler.end_headers()


def get_ICE_servers() -> None:
    return None


def parse_ice_candidates(sdp_message: str) -> list[RTCIceCandidate]:
    sdp_message = sdp_message.replace("\\r\\n", "\r\n")

    lines = sdp_message.splitlines()

    candidates: list[RTCIceCandidate] = []
    cand_str = "a=candidate:"
    mid_str = "a=mid:"
    mid = ""
    for line in lines:
        if line.startswith(mid_str):
            mid = line[len(mid_str) :]
        elif line.startswith(cand_str):
            candidate_str = line[len(cand_str) :]
            candidate: RTCIceCandidate = sdp.candidate_from_sdp(candidate_str)
            candidate.sdpMid = mid
            candidates.append(candidate)
    return candidates


class PicameraStreamTrack(MediaStreamTrack, Output):
    kind = "video"

    def __init__(self) -> None:
        super().__init__()
        self.img_queue: deque[tuple[bytes, bool, int | None]] = deque(maxlen=60)
        from spyglass.server.http_server import StreamingHandler

        asyncio.set_event_loop(StreamingHandler.loop)
        self.condition: asyncio.Condition = asyncio.Condition()

    def outputframe(
        self,
        frame: bytes,
        keyframe: bool = True,
        timestamp: int | None = None,
        packet: Packet | None = None,
        audio: bool = False,
    ) -> None:
        from spyglass.server.http_server import StreamingHandler

        asyncio.run_coroutine_threadsafe(
            self.put_frame(frame, keyframe, timestamp), StreamingHandler.loop
        )

    async def put_frame(
        self, frame: bytes, keyframe: bool = True, timestamp: int | None = None
    ) -> None:
        async with self.condition:
            self.img_queue.append((frame, keyframe, timestamp))
            self.condition.notify_all()

    async def recv(self) -> Packet:
        async with self.condition:

            def not_empty() -> bool:
                return len(self.img_queue) > 0

            await self.condition.wait_for(not_empty)
        img, keyframe, pts = self.img_queue.popleft()
        packet: Packet = Packet(img)
        packet.pts = pts
        packet.time_base = Fraction(1, 1000000)
        packet.is_keyframe = keyframe
        return packet
