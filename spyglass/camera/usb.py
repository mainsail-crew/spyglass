from spyglass import camera
from spyglass.server.http_server import StreamingHandler

class USB(camera.Camera):
    def start_and_run_server(self,
            bind_address,
            port,
            stream_url='/stream',
            snapshot_url='/snapshot',
            webrtc_url='/webrtc',
            orientation_exif=0):
        def get_frame(inner_self):
            #TODO: Cuts framerate in 1/n with n streams open, add some kind of buffer
            return self.picam2.capture_buffer()

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
        self.picam2.stop()
