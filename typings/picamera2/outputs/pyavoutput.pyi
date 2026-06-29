from .output import Output as Output
from _typeshed import Incomplete

class PyavOutput(Output):
    _output_name: Incomplete
    _format: Incomplete
    _streams: Incomplete
    _container: Incomplete
    _options: Incomplete
    error_callback: Incomplete
    needs_add_stream: bool
    _seen_keyframe: Incomplete
    def __init__(self, output_name, format=None, pts=None, options=None) -> None: ...
    def _add_stream(self, encoder_stream, codec_name, **kwargs) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def outputframe(self, frame, keyframe: bool = True, timestamp=None, packet=None, audio: bool = False) -> None: ...
