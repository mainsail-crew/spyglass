from enum import Enum
from types import ModuleType

class _QT_BINDING(Enum):
    PyQt5 = 'PyQt5'
    PyQt6 = 'PyQt6'
    PySide2 = 'PySide2'
    PySide6 = 'PySide6'

def _get_qt_modules(qt_module: _QT_BINDING) -> tuple[ModuleType, ModuleType, ModuleType]: ...
