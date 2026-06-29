import ctypes
from _typeshed import Incomplete

_log: Incomplete
heapNames: Incomplete

class dma_buf_sync(ctypes.Structure):
    _fields_: Incomplete

DMA_BUF_SYNC_READ: Incomplete
DMA_BUF_SYNC_WRITE: Incomplete
DMA_BUF_SYNC_RW = DMA_BUF_SYNC_READ | DMA_BUF_SYNC_WRITE
DMA_BUF_SYNC_START: Incomplete
DMA_BUF_SYNC_END: Incomplete
DMA_BUF_BASE: str
DMA_BUF_IOCTL_SYNC: Incomplete
DMA_BUF_SET_NAME: Incomplete

class dma_heap_allocation_data(ctypes.Structure):
    _fields_: Incomplete

DMA_HEAP_IOC_MAGIC: str
DMA_HEAP_IOCTL_ALLOC: Incomplete

class UniqueFD:
    __fd: Incomplete
    def __init__(self, fd: int = -1) -> None: ...
    def release(self): ...
    def get(self): ...
    def isValid(self): ...

class DmaHeap:
    __dmaHeapHandle: Incomplete
    def __init__(self) -> None: ...
    @property
    def isValid(self): ...
    def alloc(self, name, size) -> UniqueFD: ...
    def close(self) -> None: ...
