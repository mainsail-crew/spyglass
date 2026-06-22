"""Reference-counted lazy start/stop wrappers for picamera2.

CameraSession wraps Picamera2.start()/stop(): the camera only runs while
at least one consumer (encoder) holds a reference.

LazyEncoder wraps Picamera2.start_encoder()/stop_encoder(): the encoder
only runs while at least one consumer (HTTP stream / snapshot / WebRTC
peer connection) holds a reference. Each LazyEncoder also holds a
reference on the CameraSession while running, so the camera itself
turns off when no encoders are active.

LazyEncoder supports a ``linger_seconds`` parameter:

* ``< 0`` keeps the encoder running once started; subsequent releases that
  drive the ref-count to zero do not stop it. Useful for the MJPEG path
  when paired with a startup pre-warm so e.g. timelapse snapshots stay on
  the warm path.
* ``0`` stops the encoder immediately when the last consumer releases.
* ``> 0`` schedules a delayed stop; a fresh acquire within the window
  cancels the pending stop. Useful to bridge brief reconnects without
  paying the cold-start cost on every reconnect.
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
            if self._refs > 1:
                return
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
    def __init__(
        self,
        picam2,
        encoder_factory,
        output,
        session=None,
        linger_seconds=0,
    ):
        """
        :param picam2: the Picamera2 instance to start/stop the encoder on.
        :param encoder_factory: zero-arg callable returning a fresh Encoder.
        :param output: the picamera2 Output to attach to the encoder.
        :param session: optional CameraSession. If provided, the camera is
            started/stopped together with the encoder so the camera only runs
            when at least one encoder is active.
        :param linger_seconds: behavior when the last consumer releases. ``0``
            stops immediately; ``>0`` schedules a stop that is cancelled if a
            new consumer acquires within the window; ``<0`` keeps the encoder
            running forever after the first start.
        """
        self._picam2 = picam2
        self._encoder_factory = encoder_factory
        self._output = output
        self._session = session
        self._linger_seconds = linger_seconds
        self._encoder = None
        self._refs = 0
        self._lock = threading.Lock()
        self._stop_timer = None
        self._stop_token = 0

    def acquire(self):
        with self._lock:
            self._cancel_linger_locked()
            self._refs += 1
            if self._encoder is not None:
                return
            session_acquired = False
            try:
                if self._session is not None:
                    self._session.acquire()
                    session_acquired = True
                self._encoder = self._encoder_factory()
                self._picam2.start_encoder(self._encoder, self._output)
            except Exception:
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
            if self._refs > 0 or self._linger_seconds < 0:
                return
            if self._linger_seconds == 0:
                self._stop_now_locked()
            else:
                self._schedule_linger_locked()

    def _stop_now_locked(self):
        encoder = self._encoder
        self._encoder = None
        try:
            self._picam2.stop_encoder(encoder)
        finally:
            if self._session is not None:
                self._session.release()

    def _cancel_linger_locked(self):
        if self._stop_timer is None:
            return
        self._stop_timer.cancel()
        self._stop_timer = None
        self._stop_token += 1

    def _schedule_linger_locked(self):
        self._stop_token += 1
        token = self._stop_token
        timer = threading.Timer(
            self._linger_seconds, self._linger_callback, args=(token,)
        )
        timer.daemon = True
        self._stop_timer = timer
        timer.start()

    def _linger_callback(self, token):
        with self._lock:
            if self._stop_token != token:
                return
            self._stop_timer = None
            if self._refs == 0 and self._encoder is not None:
                self._stop_now_locked()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *exc):
        self.release()
