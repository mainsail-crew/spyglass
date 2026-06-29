from picamera2.previews.null_preview import *
from _typeshed import Incomplete

class DrmManager:
    lock: Incomplete
    use_count: int
    def __init__(self) -> None: ...
    card: Incomplete
    resman: Incomplete
    crtc: Incomplete
    def add(self, drm_preview) -> None: ...
    def remove(self, drm_preview) -> None: ...

class DrmPreview(NullPreview):
    FMT_MAP: Incomplete
    _manager: Incomplete
    stop_count: int
    fb: Incomplete
    mem: Incomplete
    fd: Incomplete
    def __init__(self, x: int = 0, y: int = 0, width: int = 640, height: int = 480, transform=None) -> None: ...
    current: Incomplete
    own_current: Incomplete
    def render_request(self, completed_request) -> None: ...
    def handle_request(self, picam2) -> None: ...
    plane: Incomplete
    drmfbs: Incomplete
    window: Incomplete
    transform: Incomplete
    overlay_plane: Incomplete
    overlay_fb: Incomplete
    overlay_new_fb: Incomplete
    lock: Incomplete
    display_stream_name: Incomplete
    def init_drm(self, x, y, width, height, transform) -> None: ...
    def set_overlay(self, overlay) -> None: ...
    def render_drm(self, picam2, completed_request) -> None: ...
    def stop(self) -> None: ...
