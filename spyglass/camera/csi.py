import io
from threading import Condition

import libcamera
from picamera2.encoders import _hw_encoder_available
from picamera2.outputs import FileOutput

from spyglass import WEBRTC_ENABLED, camera, logger
from spyglass.camera.lazy_encoder import CameraSession, LazyEncoder
from spyglass.server.http_server import StreamingHandler

# Preference ordered pixel formats accepted by the picamera2 V4L2 HW and
# JpegEncoder SW encoders.
_PREFERRED_MAIN_STREAM_FORMATS = (
    "YUV420",
    "BGR888",
    "RGB888",
    "XBGR8888",
    "XRGB8888",
)


class CSI(camera.Camera):
    def _main_stream_config(self, width: int, height: int) -> dict:
        cfg = super()._main_stream_config(width, height)
        chosen = self._pick_main_stream_format()
        if chosen is not None:
            cfg["format"] = chosen
        return cfg

    def _pick_main_stream_format(self) -> str | None:
        """Return the highest-priority encoder-compatible format the camera
        actually supports, or ``None`` to defer to the picamera2 default."""
        supported = self._enumerate_supported_main_stream_formats()
        if not supported:
            return None

        preferred_fmts = (f for f in _PREFERRED_MAIN_STREAM_FORMATS if f in supported)
        fmt = next(preferred_fmts, None)

        logger.info("Supported formats: %s", sorted(supported))
        if fmt is None:
            logger.warning(
                "Camera reports no encoder-compatible main-stream formats; using picamera2 default.",
            )
            return None

        logger.info(f"Main stream using %r.", fmt)
        return fmt

    def _enumerate_supported_main_stream_formats(self) -> set[str]:
        try:
            libcamera_cfg = self.picam2.camera.generate_configuration(
                [libcamera.StreamRole.VideoRecording]
            )
            return {str(pf) for pf in libcamera_cfg.at(0).formats.pixel_formats}
        except Exception as exc:
            logger.warning(
                "Could not enumerate supported main-stream formats from libcamera "
                "(%s); using picamera2 default.",
                exc,
            )
            return set()

    def start_and_run_server(
        self,
        bind_address,
        port,
        stream_url="/?action=stream",
        snapshot_url="/?action=snapshot",
        webrtc_url="/webrtc",
        orientation_exif=0,
        use_sw_encoding=False,
        mjpeg_linger_seconds=-1,
        webrtc_linger_seconds=5,
    ):
        if _hw_encoder_available and not use_sw_encoding:
            from picamera2.encoders import MJPEGEncoder
        else:
            from picamera2.encoders import JpegEncoder as MJPEGEncoder

        class StreamingOutput(io.BufferedIOBase):
            def __init__(self):
                self.frame = None
                self.condition = Condition()

            def write(self, buf):
                with self.condition:
                    self.frame = buf
                    self.condition.notify_all()

        output = StreamingOutput()

        def get_frame(inner_self):
            with output.condition:
                output.condition.wait()
                return output.frame

        session = CameraSession(self.picam2)
        mjpeg_encoder = LazyEncoder(
            self.picam2,
            MJPEGEncoder,
            FileOutput(output),
            session=session,
            linger_seconds=mjpeg_linger_seconds,
        )
        StreamingHandler.mjpeg_encoder = mjpeg_encoder
        if WEBRTC_ENABLED:
            from picamera2.encoders import H264Encoder

            h264_encoder = LazyEncoder(
                self.picam2,
                H264Encoder,
                self.media_track,
                session=session,
                linger_seconds=webrtc_linger_seconds,
            )
            StreamingHandler.h264_encoder = h264_encoder
        else:
            StreamingHandler.h264_encoder = None

        if mjpeg_linger_seconds < 0:
            mjpeg_encoder.acquire()
        if WEBRTC_ENABLED and webrtc_linger_seconds < 0:
            h264_encoder.acquire()

        self._run_server(
            bind_address,
            port,
            StreamingHandler,
            get_frame,
            stream_url=stream_url,
            snapshot_url=snapshot_url,
            webrtc_url=webrtc_url,
            orientation_exif=orientation_exif,
        )

    def stop(self):
        try:
            self.picam2.stop_encoder()
        except Exception:
            pass
        try:
            self.picam2.stop()
        except Exception:
            pass
