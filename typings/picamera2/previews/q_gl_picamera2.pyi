from _typeshed import Incomplete
from OpenGL.EGL.EXT.image_dma_buf_import import *
from OpenGL.EGL.KHR.image import *
from OpenGL.EGL.VERSION.EGL_1_0 import *
from OpenGL.EGL.VERSION.EGL_1_2 import *
from OpenGL.EGL.VERSION.EGL_1_3 import *
from OpenGL.GLES2.OES.EGL_image import *
from OpenGL.GLES2.OES.EGL_image_external import *
from OpenGL.GLES2.VERSION.GLES2_2_0 import *
from OpenGL.GLES3.VERSION.GLES3_3_0 import *
from picamera2.previews.gl_helpers import *

from .qt_compatibility import _QT_BINDING as _QT_BINDING
from .qt_compatibility import _get_qt_modules as _get_qt_modules

class EglState:
    max_texture_size: Incomplete
    def __init__(self) -> None: ...
    display: Incomplete
    def create_display(self) -> None: ...
    config: Incomplete
    def choose_config(self) -> None: ...
    context: Incomplete
    def create_context(self) -> None: ...

def _get_qglpicamera2(qt_module: _QT_BINDING): ...

QPicamera2: Incomplete
