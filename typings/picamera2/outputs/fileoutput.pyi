from _typeshed import Incomplete

from .output import Output as Output

class FileOutput(Output):
    dead: bool
    _firstframe: bool
    _before: Incomplete
    _connectiondead: Incomplete
    _splitsize: Incomplete
    def __init__(self, file=None, pts=None, split=None) -> None: ...
    @property
    def fileoutput(self): ...
    _split: bool
    _needs_close: bool
    _fileoutput: Incomplete
    @fileoutput.setter
    def fileoutput(self, file) -> None: ...
    @property
    def connectiondead(self): ...
    @connectiondead.setter
    def connectiondead(self, _callback) -> None: ...
    def outputframe(
        self,
        frame,
        keyframe: bool = True,
        timestamp=None,
        packet=None,
        audio: bool = False,
    ) -> None: ...
    def stop(self) -> None: ...
    def close(self) -> None: ...
    def _write(self, frame, timestamp=None) -> None: ...
