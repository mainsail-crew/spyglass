"""init py module."""
import logging
import importlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if importlib.util.find_spec("aiortc"):
    AIORTC_AVAILABLE=True
else:
    AIORTC_AVAILABLE=False
