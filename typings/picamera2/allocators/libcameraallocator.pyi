from _typeshed import Incomplete
from picamera2.allocators.allocator import Allocator as Allocator

_log: Incomplete

class LibcameraAllocator(Allocator):
    needs_sync: bool
    camera: Incomplete
    def __init__(self, camera) -> None: ...
    allocator: Incomplete
    def allocate(self, libcamera_config, _) -> None: ...
    def buffers(self, stream): ...
