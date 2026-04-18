"""init py module."""

import importlib.util
import logging

from picamera2.encoders import _hw_encoder_available

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WEBRTC_ENABLED = False
if importlib.util.find_spec("aiortc"):
    WEBRTC_ENABLED = _hw_encoder_available


def set_webrtc_enabled(enabled):
    global WEBRTC_ENABLED
    WEBRTC_ENABLED = enabled
