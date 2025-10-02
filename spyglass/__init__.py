"""init py module."""

import importlib.util
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if importlib.util.find_spec("aiortc"):
    WEBRTC_ENABLED = True
else:
    WEBRTC_ENABLED = False


def set_webrtc_enabled(enabled):
    global WEBRTC_ENABLED
    WEBRTC_ENABLED = enabled
