from _typeshed import Incomplete
from picamera2.encoders.encoder import Encoder as Encoder
from picamera2.encoders.encoder import Quality as Quality

from ..request import MappedArray as MappedArray

class LibavH264Encoder(Encoder):
    _codec: str
    repeat: Incomplete
    bitrate: Incomplete
    iperiod: Incomplete
    framerate: Incomplete
    qp: Incomplete
    profile: Incomplete
    preset: Incomplete
    drop_final_frames: bool
    threads: int
    _lasttimestamp: Incomplete
    _use_hw: bool
    _request_release_delay: int
    _request_release_queue: Incomplete
    _key_frames_requested: int
    _key_frames_generated: int
    def __init__(
        self,
        bitrate=None,
        repeat: bool = True,
        iperiod: int = 30,
        framerate: int = 30,
        qp=None,
        profile=None,
    ) -> None: ...
    @property
    def use_hw(self): ...
    @use_hw.setter
    def use_hw(self, value) -> None: ...
    def _setup(self, quality) -> None: ...
    def _send_streams(self, output) -> None: ...
    _container: Incomplete
    _stream: Incomplete
    _av_input_format: Incomplete
    def _start(self) -> None: ...
    def _stop(self) -> None: ...
    def _encode(self, stream, request) -> None: ...
    def force_key_frame(self) -> None: ...
