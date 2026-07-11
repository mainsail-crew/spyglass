from picamera2.encoders import Quality

from spyglass import camera, logger
from spyglass.camera.camera import ServerConfig
from spyglass.server.http_server import StreamingHandler


class USB(camera.Camera):
    def start_and_run_server(
        self,
        config: ServerConfig,
        use_sw_encoding: bool = False,
        mjpeg_linger_seconds: float = -1,
        webrtc_linger_seconds: float = 5,
        mjpg_quality: Quality | None = None,
        h264_quality: Quality | None = None,
    ) -> None:
        def get_frame(inner_self: StreamingHandler) -> bytes:
            # TODO: Cuts framerate in 1/n with n streams open, add some kind of buffer
            return self.picam2.capture_buffer()

        if use_sw_encoding:
            logger.warning(
                "Using software encoding is not supported for USB cameras and will be ignored!"
            )
        if mjpeg_linger_seconds != -1 or webrtc_linger_seconds != 5:
            logger.warning(
                "Using linger seconds is not supported for USB cameras and will be ignored!"
            )
        if mjpg_quality is not None or h264_quality is not None:
            logger.warning(
                "Setting quality is not supported for USB cameras and will be ignored!"
            )

        self.picam2.start()

        self._run_server(config, StreamingHandler, get_frame)

    def stop(self) -> None:
        self.picam2.stop()
