from videodev2 import *
from _typeshed import Incomplete
from picamera2.encoders.encoder import Encoder as Encoder

class V4L2Encoder(Encoder):
    bufs: Incomplete
    bitrate: Incomplete
    _pixformat: Incomplete
    _controls: Incomplete
    vd: Incomplete
    framerate: Incomplete
    _enable_framerate: bool
    _key_frames_requested: int
    _key_frames_generated: int
    def __init__(self, bitrate, pixformat) -> None: ...
    @property
    def _v4l2_format(self): ...
    buf_available: Incomplete
    buf_frame: Incomplete
    thread: Incomplete
    def _start(self) -> None: ...
    def _stop(self) -> None: ...
    def _check_for_picture(self, buf): ...
    def thread_poll(self, buf_available) -> None: ...
    def _encode(self, stream, request) -> None: ...
