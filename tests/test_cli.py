import argparse
import pytest
from unittest.mock import MagicMock, ANY, patch

AF_SPEED_ENUM_NORMAL = 1
AF_SPEED_ENUM_FAST = 2
AF_MODE_ENUM_CONTINUOUS = 2
AF_MODE_ENUM_MANUAL = 3

DEFAULT_HEIGHT = 480
DEFAULT_WIDTH = 640
DEFAULT_FLIP_VERTICALLY = False
DEFAULT_FLIP_HORIZONTALLY = False
DEFAULT_UPSIDE_DOWN = False
DEFAULT_LENS_POSITION = 0.0
DEFAULT_FPS = 15
DEFAULT_AF_SPEED = AF_SPEED_ENUM_NORMAL
DEFAULT_AUTOFOCUS_MODE = AF_MODE_ENUM_CONTINUOUS
DEFAULT_CONTROLS = []
DEFAULT_TUNING_FILTER = None
DEFAULT_TUNING_FILTER_DIR = None
DEFAULT_CAMERA_NUM = 0


@pytest.fixture(autouse=True)
def mock_libraries(mocker):
    mock_libcamera = MagicMock()
    mock_picamera2 = MagicMock()
    mock_picamera2_encoders = MagicMock()
    mock_picamera2_outputs = MagicMock()
    mock_picamera2_outputs.Output = MagicMock
    mocker.patch.dict('sys.modules', {
        'libcamera': mock_libcamera,
        'picamera2': mock_picamera2,
        'picamera2.encoders': mock_picamera2_encoders,
        'picamera2.outputs': mock_picamera2_outputs,
    })
    mocker.patch('libcamera.controls.AfModeEnum.Manual', AF_MODE_ENUM_MANUAL)
    mocker.patch('libcamera.controls.AfModeEnum.Continuous', AF_MODE_ENUM_CONTINUOUS)
    mocker.patch('libcamera.controls.AfSpeedEnum.Normal', AF_SPEED_ENUM_NORMAL)
    mocker.patch('libcamera.controls.AfSpeedEnum.Fast', AF_SPEED_ENUM_FAST)


def test_parse_bindaddress():
    from spyglass import cli
    args = cli.get_args(['-b', '1.2.3.4'])
    assert args.bindaddress == '1.2.3.4'


def test_parse_port():
    from spyglass import cli
    args = cli.get_args(['-p', '123'])
    assert args.port == 123


def test_parse_resolution():
    from spyglass import cli
    args = cli.get_args(['-r', '100x200'])
    assert args.resolution == '100x200'


def test_split_resolution():
    from spyglass import cli
    (width, height) = cli.split_resolution('100x200')
    assert width == 100
    assert height == 200


def test_parse_tuning_filter():
    from spyglass import cli
    args = cli.get_args(['-tf', 'filter'])
    assert args.tuning_filter == 'filter'


def test_parse_tuning_filter_dir():
    from spyglass import cli
    args = cli.get_args(['-tfd', 'dir'])
    assert args.tuning_filter_dir == 'dir'


@patch("spyglass.camera.init_camera")
def test_init_camera_with_defaults(mock_spyglass_camera,):
    from spyglass import cli
    cli.main(args=[])
    mock_spyglass_camera.assert_called_once_with(
        DEFAULT_CAMERA_NUM,
        DEFAULT_TUNING_FILTER,
        DEFAULT_TUNING_FILTER_DIR
    )

@patch("spyglass.camera.init_camera")
def test_configure_with_defaults(mock_init_camera):
    from spyglass import cli
    cli.main(args=[])
    cam_instance = mock_init_camera.return_value
    cam_instance.configure.assert_called_once_with(
        DEFAULT_WIDTH,
        DEFAULT_HEIGHT,
        DEFAULT_FPS,
        DEFAULT_AUTOFOCUS_MODE,
        DEFAULT_LENS_POSITION,
        DEFAULT_AF_SPEED,
        DEFAULT_CONTROLS,
        DEFAULT_UPSIDE_DOWN,
        DEFAULT_FLIP_HORIZONTALLY,
        DEFAULT_FLIP_VERTICALLY
    )

@patch("spyglass.camera.init_camera")
def test_configure_with_parameters(mock_init_camera):
    from spyglass import cli
    cli.main(args=[
        '-n', '1',
        '-tf', 'test',
        '-tfd', 'test-dir',
        '-r', '200x100',
        '-f', '20',
        '-af', 'manual',
        '-l', '1.0',
        '-s', 'normal',
        '-ud', '-fh', '-fv',
        '-c', 'brightness=-0.4',
        '-c', 'awbenable=false',
    ])
    cam_instance = mock_init_camera.return_value
    cam_instance.configure.assert_called_once_with(
        200,
        100,
        20,
        AF_MODE_ENUM_MANUAL,
        1.0,
        AF_SPEED_ENUM_NORMAL,
        [['brightness', '-0.4'],['awbenable', 'false']],
        True,
        True,
        True
    )


def test_raise_error_when_width_greater_than_maximum():
    from spyglass import cli
    with pytest.raises(argparse.ArgumentTypeError):
        cli.main(args=[
            '-r', '1921x1920'
        ])


def test_raise_error_when_height_greater_than_maximum():
    from spyglass import cli
    with pytest.raises(argparse.ArgumentTypeError):
        cli.main(args=[
            '-r', '1920x1921'
        ])


@patch("spyglass.camera.init_camera")
def test_configure_camera_af_continuous_speed_fast(mock_init_camera):
    from spyglass import cli
    cli.main(args=[
        '-af', 'continuous',
        '-s', 'fast'
    ])
    cam_instance = mock_init_camera.return_value
    cam_instance.configure.assert_called_once_with(
        DEFAULT_WIDTH,
        DEFAULT_HEIGHT,
        DEFAULT_FPS,
        AF_MODE_ENUM_CONTINUOUS,
        DEFAULT_LENS_POSITION,
        AF_SPEED_ENUM_FAST,
        DEFAULT_CONTROLS,
        DEFAULT_UPSIDE_DOWN,
        DEFAULT_FLIP_HORIZONTALLY,
        DEFAULT_FLIP_VERTICALLY
    )


@patch("spyglass.camera.init_camera")
def test_run_server_with_configuration_from_arguments(mock_init_camera):
    from spyglass import cli
    cli.main(args=[
        '-b', '1.2.3.4',
        '-p', '1234',
        '-st', 'streaming-url',
        '-sn', 'snapshot-url',
        '-w', 'webrtc-url',
        '-or', 'h',
        '-sw'
    ])
    cam_instance = mock_init_camera.return_value
    cam_instance.start_and_run_server.assert_called_once_with(
        '1.2.3.4',
        1234,
        'streaming-url',
        'snapshot-url',
        'webrtc-url',
        1,
        True
    )


@patch("spyglass.camera.init_camera")
@pytest.mark.parametrize("input_value, expected_output", [
    ('h', 1),
    ('mh', 2),
    ('r180', 3),
    ('mv', 4),
    ('mhr270', 5),
    ('r90', 6),
    ('mhr90', 7),
    ('r270', 8),
])
def test_run_server_with_orientation(mock_init_camera, input_value, expected_output):
    from spyglass import cli
    cli.main(args=[
        '-b', '1.2.3.4',
        '-p', '1234',
        '-st', 'streaming-url',
        '-sn', 'snapshot-url',
        '-w', 'webrtc-url',
        '-or', input_value,
        '-sw'
    ])
    cam_instance = mock_init_camera.return_value
    cam_instance.start_and_run_server.assert_called_once_with(
        '1.2.3.4',
        1234,
        'streaming-url',
        'snapshot-url',
        'webrtc-url',
        expected_output,
        True
    )
