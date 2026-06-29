from .output import Output as Output
from _typeshed import Incomplete

class FfmpegOutput(Output):
    ffmpeg: Incomplete
    output_broken: bool
    output_filename: Incomplete
    audio: Incomplete
    audio_device: Incomplete
    audio_filter: Incomplete
    audio_sync: Incomplete
    audio_samplerate: Incomplete
    audio_codec: Incomplete
    audio_bitrate: Incomplete
    timeout: Incomplete
    error_callback: Incomplete
    needs_pacing: bool
    def __init__(self, output_filename, audio: bool = False, audio_device: str = 'default', audio_sync: float = -0.3, audio_samplerate: int = 48000, audio_codec: str = 'aac', audio_bitrate: int = 128000, audio_filter=None, pts=None) -> None: ...
    def start(self): ...
    def stop(self) -> None: ...
    def outputframe(self, frame, keyframe: bool = True, timestamp=None, packet=None, audio: bool = False) -> None: ...
