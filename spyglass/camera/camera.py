import threading
from abc import ABC, abstractmethod

import libcamera
from picamera2 import Picamera2

from spyglass import WEBRTC_ENABLED, logger
from spyglass.camera_options import process_controls
from spyglass.exif import create_exif_header
from spyglass.server.http_server import StreamingHandler, StreamingServer
from spyglass.server.webrtc_whep import PicameraStreamTrack


class Camera(ABC):
    def __init__(self, picam2: Picamera2):
        self.picam2 = picam2
        self.media_track = PicameraStreamTrack()

    def create_controls(
        self, fps: int, autofocus: str, lens_position: float, autofocus_speed: str
    ):
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
        autofocus: str,
        lens_position: float,
        autofocus_speed: str,
        control_list: list[list[str]] = [],
        upsidedown=False,
        flip_horizontal=False,
        flip_vertical=False,
    ):
        controls = self.create_controls(fps, autofocus, lens_position, autofocus_speed)
        c = process_controls(self.picam2, [tuple(ctrl) for ctrl in control_list])
        controls.update(c)

        transform = libcamera.Transform(
            hflip=int(flip_horizontal or upsidedown),
            vflip=int(flip_vertical or upsidedown),
        )

        self.picam2.configure(
            self.picam2.create_video_configuration(
                main={"size": (width, height)}, controls=controls, transform=transform
            )
        )

    def _run_server(
        self,
        bind_address,
        port,
        streaming_handler: StreamingHandler,
        get_frame,
        stream_url="/stream",
        snapshot_url="/snapshot",
        webrtc_url="/webrtc",
        orientation_exif=0,
    ):
        logger.info(f"Server listening on {bind_address}:{port}")
        logger.info(f"Streaming endpoint: {stream_url}")
        logger.info(f"Snapshot endpoint: {snapshot_url}")
        if WEBRTC_ENABLED:
            logger.info(f"WebRTC endpoint: {webrtc_url}")
        logger.info("Controls endpoint: /controls")
        address = (bind_address, port)
        streaming_handler.picam2 = self.picam2
        streaming_handler.media_track = self.media_track
        streaming_handler.get_frame = get_frame
        streaming_handler.stream_url = stream_url
        streaming_handler.snapshot_url = snapshot_url
        streaming_handler.webrtc_url = webrtc_url

        if orientation_exif > 0:
            streaming_handler.exif_header = create_exif_header(orientation_exif)
        else:
            streaming_handler.exif_header = None
        current_server = StreamingServer(address, streaming_handler)
        async_loop = threading.Thread(target=StreamingHandler.loop.run_forever)
        async_loop.start()
        current_server.serve_forever()

    @abstractmethod
    def start_and_run_server(
        self,
        bind_address,
        port,
        stream_url="/stream",
        snapshot_url="/snapshot",
        webrtc_url="/webrtc",
        orientation_exif=0,
        use_sw_jpg_encoding=False,
    ):
        pass

    @abstractmethod
    def stop(self):
        pass
