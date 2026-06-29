from _typeshed import Incomplete
from picamera2.encoders import Quality as Quality
from picamera2.encoders.multi_encoder import MultiEncoder as MultiEncoder
from picamera2.request import MappedArray as MappedArray

class JpegEncoder(MultiEncoder):
    FORMAT_TABLE: Incomplete
    q: Incomplete
    colour_space: Incomplete
    colour_subsampling: Incomplete
    def __init__(self, num_threads: int = 4, q=None, colour_space=None, colour_subsampling: str = '420') -> None: ...
    def encode_func(self, request, name): ...
    def _setup(self, quality) -> None: ...
