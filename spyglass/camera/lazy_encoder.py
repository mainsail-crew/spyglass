"""Reference-counted lazy start/stop wrappers for picamera2.

CameraSession wraps Picamera2.start()/stop(): the camera only runs while
at least one consumer (encoder) holds a reference.

LazyEncoder wraps Picamera2.start_encoder()/stop_encoder(): the encoder
only runs while at least one consumer (HTTP stream / snapshot / WebRTC
peer connection) holds a reference. Each LazyEncoder also holds a
reference on the CameraSession while running, so the camera itself
turns off when no encoders are active.
"""

import threading


class CameraSession:
    def __init__(self, picam2):
        self._picam2 = picam2
        self._refs = 0
        self._lock = threading.Lock()

    def acquire(self):
        with self._lock:
            self._refs += 1
            if self._refs == 1:
                try:
                    self._picam2.start()
                except Exception:
                    self._refs -= 1
                    raise

    def release(self):
        with self._lock:
            if self._refs == 0:
                return
            self._refs -= 1
            if self._refs == 0:
                self._picam2.stop()


class LazyEncoder:
    def __init__(self, picam2, encoder_factory, output, session=None):
        """
        :param picam2: the Picamera2 instance to start/stop the encoder on.
        :param encoder_factory: zero-arg callable returning a fresh Encoder.
        :param output: the picamera2 Output to attach to the encoder.
        :param session: optional CameraSession. If provided, the camera is
            started/stopped together with the encoder so the camera only runs
            when at least one encoder is active.
        """
        self._picam2 = picam2
        self._encoder_factory = encoder_factory
        self._output = output
        self._session = session
        self._encoder = None
        self._refs = 0
        self._lock = threading.Lock()

    def acquire(self):
        with self._lock:
            self._refs += 1
            if self._refs == 1:
                session_acquired = False
                try:
                    if self._session is not None:
                        self._session.acquire()
                        session_acquired = True
                    self._encoder = self._encoder_factory()
                    self._picam2.start_encoder(self._encoder, self._output)
                except Exception:
                    # Roll back so a future caller can retry.
                    self._refs -= 1
                    self._encoder = None
                    if session_acquired and self._session is not None:
                        self._session.release()
                    raise

    def release(self):
        with self._lock:
            if self._refs == 0:
                return
            self._refs -= 1
            if self._refs == 0 and self._encoder is not None:
                encoder = self._encoder
                self._encoder = None
                try:
                    self._picam2.stop_encoder(encoder)
                finally:
                    if self._session is not None:
                        self._session.release()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *exc):
        self.release()
