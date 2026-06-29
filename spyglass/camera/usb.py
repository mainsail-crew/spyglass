from picamera2.encoders import Quality

from spyglass import camera, logger
from spyglass.camera.camera import ServerConfig
from spyglass.server.http_server import StreamingHandler


class USB(camera.Camera):
    def start_and_run_server(
        self,
        config,
        use_sw_encoding=False,
        mjpeg_linger_seconds=-1,
        webrtc_linger_seconds=5,
        mjpg_quality: Quality | None = None,
        h264_quality: Quality | None = None,
    ):
        def get_frame(inner_self):
            # TODO: Cuts framerate in 1/n with n streams open, add some kind of buffer
            return self.picam2.capture_buffer()

        if mjpg_quality is not None or h264_quality is not None:
            logger.warning("Setting quality is not supported for USB cameras!")

        self.picam2.start()

        self._run_server(config, StreamingHandler, get_frame)

    def stop(self):
        self.picam2.stop()
