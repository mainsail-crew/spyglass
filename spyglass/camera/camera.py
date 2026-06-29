import threading
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import libcamera
from picamera2 import Picamera2
from picamera2.encoders import Quality

from spyglass import WEBRTC_ENABLED, logger
from spyglass.camera_options import process_controls
from spyglass.exif import create_exif_header
from spyglass.server.http_server import StreamingHandler, StreamingServer
from spyglass.server.webrtc_whep import PicameraStreamTrack


@dataclass
class ServerConfig:
    bind_address: str = "0.0.0.0"
    port: int = 8080
    stream_url: str = "/?action=stream"
    snapshot_url: str = "/?action=snapshot"
    webrtc_url: str = "/webrtc"
    orientation_exif: int = 0


class Camera(ABC):
    def __init__(self, picam2: Picamera2) -> None:
        self.picam2 = picam2
        self.media_track = PicameraStreamTrack()

    def create_controls(
        self,
        fps: int,
        autofocus: libcamera.controls.AfModeEnum,
        lens_position: float,
        autofocus_speed: libcamera.controls.AfSpeedEnum,
    ) -> dict[str, Any]:
        controls = {}

        if "FrameDurationLimits" in self.picam2.camera_controls:
            controls["FrameRate"] = fps

        if "AfMode" in self.picam2.camera_controls:
            controls["AfMode"] = autofocus
            controls["AfSpeed"] = autofocus_speed
            if autofocus == libcamera.controls.AfModeEnum.Manual:
                controls["LensPosition"] = lens_position
        else:
            logger.warning("Attached camera does not support autofocus")

        return controls

    def configure(
        self,
        width: int,
        height: int,
        fps: int,
        autofocus: libcamera.controls.AfModeEnum,
        lens_position: float,
        autofocus_speed: libcamera.controls.AfSpeedEnum,
        control_list: list[list[str]] = [],
        upsidedown: bool = False,
        flip_horizontal: bool = False,
        flip_vertical: bool = False,
    ) -> None:
        controls = self.create_controls(fps, autofocus, lens_position, autofocus_speed)
        c = process_controls(self.picam2, [(ctrl[0], ctrl[1]) for ctrl in control_list])
        controls.update(c)

        transform = libcamera.Transform(
            hflip=flip_horizontal or upsidedown,
            vflip=flip_vertical or upsidedown,
        )

        main_cfg = self._main_stream_config(width, height)
        self.picam2.configure(
            self.picam2.create_video_configuration(
                main=main_cfg, controls=controls, transform=transform
            )
        )

    def _main_stream_config(self, width: int, height: int) -> dict[str, Any]:
        """Picamera2 main-stream config dict. Subclasses override to pick the
        most efficient pixel format supported by their camera and encoders."""
        return {"size": (width, height)}

    def _run_server(
        self,
        config: ServerConfig,
        streaming_handler: type[StreamingHandler],
        get_frame: Callable[[StreamingHandler], bytes],
    ):
        logger.info(f"Server listening on {config.bind_address}:{config.port}")
        logger.info(f"Streaming endpoint: {config.stream_url}")
        logger.info(f"Snapshot endpoint: {config.snapshot_url}")
        if WEBRTC_ENABLED:
            logger.info(f"WebRTC endpoint: {config.webrtc_url}")
        logger.info("Controls endpoint: /controls")
        address = (config.bind_address, config.port)
        streaming_handler.picam2 = self.picam2
        streaming_handler.media_track = self.media_track
        streaming_handler.get_frame = get_frame
        streaming_handler.stream_url = config.stream_url
        streaming_handler.snapshot_url = config.snapshot_url
        streaming_handler.webrtc_url = config.webrtc_url

        streaming_handler.exif_header = None
        if config.orientation_exif > 0:
            streaming_handler.exif_header = create_exif_header(config.orientation_exif)
        current_server = StreamingServer(address, streaming_handler)
        async_loop = threading.Thread(target=StreamingHandler.loop.run_forever)
        async_loop.start()
        current_server.serve_forever()

    @abstractmethod
    def start_and_run_server(
        self,
        config: ServerConfig,
        use_sw_encoding: bool = False,
        mjpeg_linger_seconds: float = -1,
        webrtc_linger_seconds: float = 5,
        mjpg_quality: Quality | None = None,
        h264_quality: Quality | None = None,
    ) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
