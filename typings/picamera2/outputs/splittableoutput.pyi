from _typeshed import Incomplete

from .output import Output as Output

class SplittableOutput(Output):
    _output: Incomplete
    _new_output: Incomplete
    _split_done: Incomplete
    _streams: Incomplete
    needs_add_stream: bool
    def __init__(self, output=None, *args, **kwargs) -> None: ...
    _wait_for_keyframe: Incomplete
    def split_output(self, new_output, wait_for_keyframe: bool = True) -> None: ...
    def outputframe(
        self,
        frame,
        keyframe: bool = True,
        timestamp=None,
        packet=None,
        audio: bool = False,
    ) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def _add_stream(self, encoder_stream, codec_name, **kwargs) -> None: ...
