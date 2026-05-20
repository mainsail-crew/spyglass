"""Reference-counted lazy start/stop wrapper for picamera2 encoders.

The encoder is only running while at least one consumer holds a reference.
This avoids burning CPU on encoders that have no clients.
"""

import threading


class LazyEncoder:
    def __init__(self, picam2, encoder_factory, output):
        """
        :param picam2: the Picamera2 instance to start/stop the encoder on.
        :param encoder_factory: zero-arg callable returning a fresh Encoder.
        :param output: the picamera2 Output to attach to the encoder.
        """
        self._picam2 = picam2
        self._encoder_factory = encoder_factory
        self._output = output
        self._encoder = None
        self._refs = 0
        self._lock = threading.Lock()

    def acquire(self):
        with self._lock:
            self._refs += 1
            if self._refs == 1:
                try:
                    self._encoder = self._encoder_factory()
                    self._picam2.start_encoder(self._encoder, self._output)
                except Exception:
                    # Roll back so a future caller can retry.
                    self._refs -= 1
                    self._encoder = None
                    raise

    def release(self):
        with self._lock:
            if self._refs == 0:
                return
            self._refs -= 1
            if self._refs == 0 and self._encoder is not None:
                self._picam2.stop_encoder(self._encoder)
                self._encoder = None

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *exc):
        self.release()
