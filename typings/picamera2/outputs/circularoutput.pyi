from .fileoutput import FileOutput as FileOutput
from _typeshed import Incomplete

class CircularOutput(FileOutput):
    _lock: Incomplete
    outputtofile: Incomplete
    def __init__(self, file=None, pts=None, buffersize=..., outputtofile: bool = True) -> None: ...
    @property
    def buffersize(self): ...
    _buffersize: Incomplete
    _circular: Incomplete
    @buffersize.setter
    def buffersize(self, value) -> None: ...
    _firstframe: bool
    def outputframe(self, frame, keyframe: bool = True, timestamp=None, packet=None, audio: bool = False) -> None: ...
    recording: bool
    def stop(self) -> None: ...
