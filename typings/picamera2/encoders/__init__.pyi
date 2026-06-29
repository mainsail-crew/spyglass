from ..platform import Platform as Platform
from ..platform import get_platform as get_platform
from .encoder import Encoder as Encoder
from .encoder import Quality as Quality
from .h264_encoder import H264Encoder as H264Encoder
from .jpeg_encoder import JpegEncoder as JpegEncoder
from .libav_h264_encoder import LibavH264Encoder as LibavH264Encoder
from .libav_mjpeg_encoder import LibavMjpegEncoder as LibavMjpegEncoder
from .mjpeg_encoder import MJPEGEncoder as MJPEGEncoder
from .multi_encoder import MultiEncoder as MultiEncoder

_hw_encoder_available: bool
