import sys
from unittest.mock import MagicMock

AF_MODE_ENUM_MANUAL = 3
AF_SPEED_ENUM_NORMAL = 1

mock_libcamera = MagicMock()
mock_picamera2 = MagicMock()
mock_picamera2.encoders._hw_encoder_available = False
mock_picamera2.outputs.Output = MagicMock
sys.modules.update(
    {
        "libcamera": mock_libcamera,
        "picamera2": mock_picamera2,
        "picamera2.encoders": mock_picamera2.encoders,
        "picamera2.outputs": mock_picamera2.outputs,
    }
)
mock_libcamera.controls.AfModeEnum.Manual = AF_MODE_ENUM_MANUAL
mock_libcamera.controls.AfSpeedEnum.Normal = AF_SPEED_ENUM_NORMAL
mock_libcamera.StreamRole.VideoRecording = object()


def _make_picam2(supported_formats=[], enumerate_raises=None):
    """Build a mocked Picamera2 whose libcamera-level
    ``camera.generate_configuration(...)`` reports the given pixel formats."""
    picam2 = MagicMock()
    picam2.camera_controls = {}
    picam2.create_video_configuration.side_effect = lambda **kw: dict(kw)

    if enumerate_raises is not None:
        picam2.camera.generate_configuration.side_effect = enumerate_raises
    else:
        formats = MagicMock()
        formats.pixel_formats = supported_formats
        stream_cfg = MagicMock()
        stream_cfg.formats = formats
        libcam_cfg = MagicMock()
        libcam_cfg.at.return_value = stream_cfg
        picam2.camera.generate_configuration.return_value = libcam_cfg
    return picam2


def _run_configure(cam):
    cam.configure(
        width=1920,
        height=1080,
        fps=30,
        autofocus=AF_MODE_ENUM_MANUAL,
        lens_position=0.0,
        autofocus_speed=AF_SPEED_ENUM_NORMAL,
    )


def test_csi_picks_yuv420_when_supported():
    from spyglass.camera.csi import CSI

    picam2 = _make_picam2(
        supported_formats=["YUV420", "XBGR8888", "BGR888", "NV12", "RGB565"]
    )
    cam = CSI(picam2)
    _run_configure(cam)

    main = picam2.create_video_configuration.call_args.kwargs["main"]
    assert main == {"size": (1920, 1080), "format": "YUV420"}


def test_csi_falls_through_preference_when_yuv420_missing():
    from spyglass.camera.csi import CSI

    picam2 = _make_picam2(supported_formats=["XBGR8888", "BGR888", "RGB565"])
    cam = CSI(picam2)
    _run_configure(cam)

    main = picam2.create_video_configuration.call_args.kwargs["main"]
    assert main == {"size": (1920, 1080), "format": "BGR888"}


def test_csi_omits_format_when_no_encoder_compatible_supported():
    from spyglass.camera.csi import CSI

    picam2 = _make_picam2(supported_formats=["NV12", "NV21", "RGB565", "YUYV"])
    cam = CSI(picam2)
    _run_configure(cam)

    main = picam2.create_video_configuration.call_args.kwargs["main"]
    assert "format" not in main
    assert main == {"size": (1920, 1080)}


def test_csi_omits_format_when_enumeration_fails():
    from spyglass.camera.csi import CSI

    picam2 = _make_picam2(enumerate_raises=RuntimeError("camera not yet acquired"))
    cam = CSI(picam2)
    _run_configure(cam)

    main = picam2.create_video_configuration.call_args.kwargs["main"]
    assert "format" not in main


def test_base_camera_does_not_query_libcamera_formats():
    """Subclasses other than CSI (e.g. USB) should not auto-pick a format."""
    from spyglass.camera.camera import Camera

    class _StubCamera(Camera):
        def start_and_run_server(self, *args, **kwargs):
            raise NotImplementedError

        def stop(self):
            raise NotImplementedError

    picam2 = _make_picam2(supported_formats=["YUV420"])
    cam = _StubCamera(picam2)
    _run_configure(cam)

    picam2.camera.generate_configuration.assert_not_called()
    main = picam2.create_video_configuration.call_args.kwargs["main"]
    assert "format" not in main
