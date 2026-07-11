from concurrent.futures import TimeoutError as TimeoutError

from .configuration import CameraConfiguration as CameraConfiguration
from .configuration import StreamConfiguration as StreamConfiguration
from .controls import Controls as Controls
from .converters import YUV420_to_RGB as YUV420_to_RGB
from .job import CancelledError as CancelledError
from .metadata import Metadata as Metadata
from .picamera2 import Picamera2 as Picamera2
from .picamera2 import Preview as Preview
from .remote import Pool as Pool
from .remote import Process as Process
from .remote import RemoteMappedArray as RemoteMappedArray
from .remote import RemoteRequest as RemoteRequest
from .request import CompletedRequest as CompletedRequest
from .request import MappedArray as MappedArray
from .sensor_format import SensorFormat as SensorFormat

def _set_configuration_file(filename) -> None: ...
def libcamera_transforms_eq(t1, t2): ...
def libcamera_colour_spaces_eq(c1, c2): ...
def _libcamera_size_to_tuple(sz): ...
def _libcamera_rect_to_tuple(rect): ...
