"""cli entry point for spyglass.

Parse command line arguments in, invoke server.
"""

import argparse
import re
import sys
import libcamera

from spyglass import camera_options, logger, WEBRTC_ENABLED, set_webrtc_enabled
from spyglass.exif import option_to_exif_orientation
from spyglass.__version__ import __version__


MAX_WIDTH = 1920
MAX_HEIGHT = 1920


def main(args=None):
    global WEBRTC_ENABLED
    """Entry point for hello cli.

    The setup_py entry_point wraps this in sys.exit already so this effectively
    becomes sys.exit(main()).
    The __main__ entry point similarly wraps sys.exit().
    """
    logger.info(f"Spyglass {__version__}")

    if args is None:
        args = sys.argv[1:]

    parsed_args = get_args(args)

    if parsed_args.list_controls:
        controls_str = camera_options.get_libcamera_controls_string(parsed_args.camera_num)
        if not controls_str:
            print(f"Camera {parsed_args.camera_num} not found")
        else:
            print('Available controls:\n'+controls_str)
        return

    width, height = split_resolution(parsed_args.resolution)
    controls = parsed_args.controls
    if parsed_args.controls_string:
        controls += [c.split('=') for c in parsed_args.controls_string.split(',')]

    set_webrtc_enabled(WEBRTC_ENABLED and not parsed_args.disable_webrtc)

    # Has to be imported after WEBRTC_ENABLED got set correctly
    from spyglass.camera import init_camera

    cam = init_camera(
        parsed_args.camera_num,
        parsed_args.tuning_filter,
        parsed_args.tuning_filter_dir)

    cam.configure(width,
                  height,
                  parsed_args.fps,
                  parse_autofocus(parsed_args.autofocus),
                  parsed_args.lensposition,
                  parse_autofocus_speed(parsed_args.autofocusspeed),
                  controls,
                  parsed_args.upsidedown,
                  parsed_args.flip_horizontal,
                  parsed_args.flip_vertical)
    try:
        cam.start_and_run_server(parsed_args.bindaddress,
                                 parsed_args.port,
                                 parsed_args.stream_url,
                                 parsed_args.snapshot_url,
                                 parsed_args.webrtc_url,
                                 parsed_args.orientation_exif)
    finally:
        cam.stop()

# region args parsers

def resolution_type(arg_value, pat=re.compile(r"^\d+x\d+$")):
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError("invalid value: <width>x<height> expected.")
    return arg_value


def control_type(arg_value: str):
    if '=' in arg_value:
        return arg_value.split('=')
    else:
        raise argparse.ArgumentTypeError(f"invalid control: Missing value: {arg_value}")


def orientation_type(arg_value):
    if arg_value in option_to_exif_orientation:
        return option_to_exif_orientation[arg_value]
    else:
        raise argparse.ArgumentTypeError(f"invalid value: unknown orientation {arg_value}.")


def parse_autofocus(arg_value):
    if arg_value == 'manual':
        return libcamera.controls.AfModeEnum.Manual
    elif arg_value == 'continuous':
        return libcamera.controls.AfModeEnum.Continuous
    else:
        raise argparse.ArgumentTypeError("invalid value: manual or continuous expected.")


def parse_autofocus_speed(arg_value):
    if arg_value == 'normal':
        return libcamera.controls.AfSpeedEnum.Normal
    elif arg_value == 'fast':
        return libcamera.controls.AfSpeedEnum.Fast
    else:
        raise argparse.ArgumentTypeError("invalid value: normal or fast expected.")


def split_resolution(res):
    parts = res.split('x')
    w = int(parts[0])
    h = int(parts[1])
    if w > MAX_WIDTH or h > MAX_HEIGHT:
        raise argparse.ArgumentTypeError("Maximum supported resolution is 1920x1920")
    return w, h

# endregion args parsers


# region cli args

def get_args(args):
    """Parse arguments passed in from shell."""
    return get_parser().parse_args(args)


def get_parser():
    """Return ArgumentParser for hello cli."""
    parser = argparse.ArgumentParser(
        allow_abbrev=True,
        prog='spyglass',
        description='Start a webserver for Picamera2 videostreams.',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-b', '--bindaddress', type=str, default='0.0.0.0', help='Bind to address for incoming '
                                                                                 'connections')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Bind to port for incoming connections')
    parser.add_argument('-r', '--resolution', type=resolution_type, default='640x480',
                        help='Resolution of the images width x height. Maximum is 1920x1920.')
    parser.add_argument('-f', '--fps', type=int, default=15, help='Frames per second to capture')
    parser.add_argument('-st', '--stream_url', type=str, default='/stream',
                        help='Sets the URL for the mjpeg stream')
    parser.add_argument('-sn', '--snapshot_url', type=str, default='/snapshot',
                        help='Sets the URL for snapshots (single frame of stream)')
    parser.add_argument('-w', '--webrtc_url', type=str, default='/webrtc',
                        help='Sets the URL for the WebRTC stream')
    parser.add_argument('--disable_webrtc', action='store_true',
                        help='Disables WebRTC encoding (recommended on Pi5)')
    parser.add_argument('-af', '--autofocus', type=str, default='continuous', choices=['manual', 'continuous'],
                        help='Autofocus mode')
    parser.add_argument('-l', '--lensposition', type=float, default=0.0,
                        help='Set focal distance. 0 for infinite focus, 0.5 for approximate 50cm. '
                             'Only used with Autofocus manual')
    parser.add_argument('-s', '--autofocusspeed', type=str, default='normal', choices=['normal', 'fast'],
                        help='Autofocus speed. Only used with Autofocus continuous')
    parser.add_argument('-ud', '--upsidedown', action='store_true',
                        help='Rotate the image by 180° (sensor level)')
    parser.add_argument('-fh', '--flip_horizontal', action='store_true',
                        help='Mirror the image horizontally (sensor level)')
    parser.add_argument('-fv', '--flip_vertical', action='store_true',
                        help='Mirror the image vertically (sensor level)')
    parser.add_argument('-or', '--orientation_exif', type=orientation_type, default='h',
                        help='Set the image orientation using an EXIF header. This does not work with WebRTC:\n'
                             '  h      - Horizontal (normal)\n'
                             '  mh     - Mirror horizontal\n'
                             '  r180   - Rotate 180\n'
                             '  mv     - Mirror vertical\n'
                             '  mhr270 - Mirror horizontal and rotate 270 CW\n'
                             '  r90    - Rotate 90 CW\n'
                             '  mhr90  - Mirror horizontal and rotate 90 CW\n'
                             '  r270   - Rotate 270 CW'
                        )
    parser.add_argument('-c', '--controls', default=[], type=control_type, action='extend', nargs='*',
                        help='Define camera controls to start with spyglass. '
                             'Can be used multiple times.\n'
                             'Format: <control>=<value>')
    parser.add_argument('-cs', '--controls-string', default='', type=str,
                        help='Define camera controls to start with spyglass. '
                             'Input as a long string.\n'
                             'Format: <control1>=<value1> <control2>=<value2>')
    parser.add_argument('-tf', '--tuning_filter', type=str, default=None, nargs='?', const="",
                        help='Set a tuning filter file name.')
    parser.add_argument('-tfd', '--tuning_filter_dir', type=str, default=None, nargs='?',const="",
                        help='Set the directory to look for tuning filters.')
    parser.add_argument('--list-controls', action='store_true', help='List available camera controls and exits.')
    parser.add_argument('-n', '--camera_num', type=int, default=0, help='Camera number to be used (Works with --list-controls)')
    return parser

# endregion cli args
