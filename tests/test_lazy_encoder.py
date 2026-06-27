import time
from unittest.mock import MagicMock

import pytest

from spyglass.camera.lazy_encoder import CameraSession, LazyEncoder


def _make(picam2=None, *, session=None, linger_seconds=0):
    if picam2 is None:
        picam2 = MagicMock()
    if session is None:
        session = CameraSession(picam2)
    encoder_factory = MagicMock()
    output = MagicMock()
    lazy = LazyEncoder(
        picam2,
        encoder_factory,
        output,
        session=session,
        linger_seconds=linger_seconds,
    )
    return lazy, picam2, session, encoder_factory, output


def test_first_acquire_starts_session_then_encoder():
    lazy, picam2, _, factory, output = _make()
    lazy.acquire()

    picam2.start.assert_called_once_with()
    picam2.start_encoder.assert_called_once_with(
        factory.return_value, output, quality=None
    )


def test_extra_acquires_share_encoder_and_session():
    lazy, picam2, _, _, _ = _make()
    lazy.acquire()
    lazy.acquire()
    lazy.acquire()

    picam2.start.assert_called_once()
    picam2.start_encoder.assert_called_once()


def test_release_with_linger_zero_stops_immediately():
    lazy, picam2, _, _, _ = _make(linger_seconds=0)
    lazy.acquire()
    lazy.release()

    picam2.stop_encoder.assert_called_once()
    picam2.stop.assert_called_once_with()


def test_release_with_linger_negative_keeps_running():
    lazy, picam2, _, _, _ = _make(linger_seconds=-1)
    lazy.acquire()
    lazy.release()

    picam2.stop_encoder.assert_not_called()
    picam2.stop.assert_not_called()


def test_linger_negative_subsequent_acquire_does_not_restart_encoder():
    lazy, picam2, _, _, _ = _make(linger_seconds=-1)
    lazy.acquire()
    lazy.release()
    lazy.acquire()

    picam2.start.assert_called_once()
    picam2.start_encoder.assert_called_once()


def test_release_with_positive_linger_does_not_stop_immediately():
    lazy, picam2, _, _, _ = _make(linger_seconds=10)
    lazy.acquire()
    lazy.release()

    assert lazy._stop_timer is not None
    picam2.stop_encoder.assert_not_called()
    picam2.stop.assert_not_called()

    lazy._stop_timer.cancel()  # clean up so the test process exits cleanly


def test_acquire_cancels_pending_linger_stop():
    lazy, picam2, _, _, _ = _make(linger_seconds=10)
    lazy.acquire()
    lazy.release()
    assert lazy._stop_timer is not None

    lazy.acquire()
    assert lazy._stop_timer is None
    picam2.stop_encoder.assert_not_called()


def test_positive_linger_eventually_stops():
    lazy, picam2, _, _, _ = _make(linger_seconds=0.05)
    lazy.acquire()
    lazy.release()

    deadline = time.monotonic() + 1.0
    while time.monotonic() < deadline and picam2.stop_encoder.call_count == 0:
        time.sleep(0.01)

    picam2.stop_encoder.assert_called_once()
    picam2.stop.assert_called_once()


def test_release_at_zero_refs_is_noop():
    lazy, picam2, _, _, _ = _make(linger_seconds=0)
    lazy.release()  # never acquired

    picam2.start.assert_not_called()
    picam2.stop_encoder.assert_not_called()


def test_acquire_rolls_back_when_start_encoder_fails():
    picam2 = MagicMock()
    picam2.start_encoder.side_effect = RuntimeError("boom")
    lazy, _, session, _, _ = _make(picam2=picam2, linger_seconds=0)

    with pytest.raises(RuntimeError):
        lazy.acquire()

    # Both refs rolled back; camera was stopped via session.release().
    assert session._refs == 0
    picam2.start.assert_called_once()
    picam2.stop.assert_called_once()

    # A retry succeeds.
    picam2.start_encoder.side_effect = None
    lazy.acquire()
    assert picam2.start_encoder.call_count == 2


def test_release_still_releases_session_if_stop_encoder_raises():
    picam2 = MagicMock()
    picam2.stop_encoder.side_effect = RuntimeError("boom")
    lazy, _, session, _, _ = _make(picam2=picam2, linger_seconds=0)

    lazy.acquire()
    with pytest.raises(RuntimeError):
        lazy.release()

    assert session._refs == 0
    picam2.stop.assert_called_once()


def test_two_encoders_share_one_session():
    picam2 = MagicMock()
    session = CameraSession(picam2)
    mjpeg, _, _, _, _ = _make(picam2=picam2, session=session, linger_seconds=0)
    h264, _, _, _, _ = _make(picam2=picam2, session=session, linger_seconds=0)

    mjpeg.acquire()
    h264.acquire()
    picam2.start.assert_called_once()

    mjpeg.release()
    picam2.stop.assert_not_called()

    h264.release()
    picam2.stop.assert_called_once()


def test_stale_timer_callback_after_cancel_is_ignored():
    lazy, picam2, _, _, _ = _make(linger_seconds=0.05)
    lazy.acquire()
    lazy.release()
    # Acquire before the timer can fire to cancel the stop.
    lazy.acquire()

    # Give a stale callback time to try to run.
    time.sleep(0.15)

    picam2.stop_encoder.assert_not_called()
    picam2.stop.assert_not_called()


def test_reacquire_after_full_stop_starts_again():
    lazy, picam2, _, _, _ = _make(linger_seconds=0)
    lazy.acquire()
    lazy.release()
    lazy.acquire()

    assert picam2.start.call_count == 2
    assert picam2.start_encoder.call_count == 2


def test_context_manager_acquires_and_releases():
    lazy, picam2, _, _, _ = _make(linger_seconds=0)
    with lazy:
        picam2.start_encoder.assert_called_once()
        picam2.stop_encoder.assert_not_called()

    picam2.stop_encoder.assert_called_once()
