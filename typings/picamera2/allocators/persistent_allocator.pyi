from _typeshed import Incomplete
from picamera2.allocators import DmaAllocator as DmaAllocator

_log: Incomplete

class PersistentAllocator(DmaAllocator):
    buffer_key: Incomplete
    buffer_dict: Incomplete
    def __init__(self) -> None: ...
    open_fds: Incomplete
    libcamera_fds: Incomplete
    frame_buffers: Incomplete
    mapped_buffers: Incomplete
    mapped_buffers_used: Incomplete
    def allocate(self, libcamera_config, use_case) -> None: ...
    def cleanup(self) -> None: ...
    def deallocate(self, buffer_key=None) -> None: ...
    def close(self) -> None: ...
