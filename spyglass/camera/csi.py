import io

from picamera2.encoders import MJPEGEncoder, H264Encoder
from picamera2.outputs import FileOutput
from threading import Condition

from spyglass import camera, WEBRTC_ENABLED
from spyglass.server.http_server import StreamingHandler

class CSI(camera.Camera):
    def start_and_run_server(self,
            bind_address,
            port,
            stream_url='/stream',
            snapshot_url='/snapshot',
            webrtc_url='/webrtc',
            orientation_exif=0):

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

        self.picam2.start_encoder(MJPEGEncoder(), FileOutput(output))
        if WEBRTC_ENABLED:
            self.picam2.start_encoder(H264Encoder(), self.media_track)
        self.picam2.start()

        self._run_server(
            bind_address,
            port,
            StreamingHandler,
            get_frame,
            stream_url=stream_url,
            snapshot_url=snapshot_url,
            webrtc_url=webrtc_url,
            orientation_exif=orientation_exif
        )

    def stop(self):
        self.picam2.stop_recording()
