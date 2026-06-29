from _typeshed import Incomplete

from ..request import MappedArray as MappedArray
from .encoder import Encoder as Encoder
from .encoder import Quality as Quality

class LibavMjpegEncoder(Encoder):
    _codec: str
    repeat: Incomplete
    bitrate: Incomplete
    iperiod: Incomplete
    framerate: Incomplete
    qp: Incomplete
    _request_release_delay: int
    _request_release_queue: Incomplete
    def __init__(
        self,
        bitrate=None,
        repeat: bool = True,
        iperiod: int = 30,
        framerate: int = 30,
        qp=None,
    ) -> None: ...
    def _setup(self, quality) -> None: ...
    def _send_streams(self, output) -> None: ...
    _container: Incomplete
    _stream: Incomplete
    _av_input_format: Incomplete
    def _start(self) -> None: ...
    def _stop(self) -> None: ...
    def _encode(self, stream, request) -> None: ...
