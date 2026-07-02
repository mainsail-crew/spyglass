"""cli entry point for spyglass.

Parse command line arguments in, invoke server.
"""

import argparse
import re
import sys

import libcamera
from picamera2.encoders import Quality

from spyglass import WEBRTC_ENABLED, camera_options, logger, set_webrtc_enabled
from spyglass.__version__ import __version__
from spyglass.camera.camera import ServerConfig
from spyglass.exif import option_to_exif_orientation


def main(args: list[str] | None = None) -> None:
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
        controls_str = camera_options.get_libcamera_controls_string(
            parsed_args.camera_num
        )
        if not controls_str:
            print(f"Camera {parsed_args.camera_num} not found")
        else:
            print("Available controls:\n" + controls_str)
        return

    use_sw_encoding = parsed_args.use_sw_encoding
    width, height = split_resolution(parsed_args.resolution)

    if not use_sw_encoding and int(width) > 1920 and int(height) > 1080:
        logger.warning(
            "Potential crash detected. Please reduce resolution to 1920x1080 or "
            "lower to stay within hardware constraints."
        )

    controls = parsed_args.controls
    if parsed_args.controls_string:
        controls += [c.split("=") for c in parsed_args.controls_string.split(",")]

    set_webrtc_enabled(
        parsed_args.force_webrtc or (WEBRTC_ENABLED and not use_sw_encoding)
    )

    # Has to be imported after WEBRTC_ENABLED got set correctly
    from spyglass.camera import init_camera

    device_path = parsed_args.device_path
    camera_num = parsed_args.camera_num
    if device_path:
        from picamera2 import Picamera2

        devices = Picamera2.global_camera_info()
        # Picamera2 is using different enumeration than libcamera
        # Therefore device["Num"] does not have to be the same as camera_num
        camera_num = None
        for index, device in enumerate(devices):
            if device["Id"] == device_path:
                camera_num = index
                break
        if camera_num is None:
            logger.error(f"No libcamera for path {device_path} found!")
            return

    cam = init_camera(
        camera_num, parsed_args.tuning_filter, parsed_args.tuning_filter_dir
    )

    server_config = ServerConfig(
        parsed_args.bindaddress,
        parsed_args.port,
        parsed_args.stream_url,
        parsed_args.snapshot_url,
        parsed_args.webrtc_url,
        parsed_args.orientation_exif,
    )

    cam.configure(
        width,
        height,
        parsed_args.fps,
        parse_autofocus(parsed_args.autofocus),
        parsed_args.lensposition,
        parse_autofocus_speed(parsed_args.autofocusspeed),
        controls,
        parsed_args.upsidedown,
        parsed_args.flip_horizontal,
        parsed_args.flip_vertical,
    )
    try:
        cam.start_and_run_server(
            server_config,
            use_sw_encoding,
            parsed_args.mjpeg_linger_seconds,
            parsed_args.webrtc_linger_seconds,
            parsed_args.mjpg_quality,
            parsed_args.h264_quality,
        )
    finally:
        cam.stop()


# region args parsers


def resolution_type(arg_value: str, pat: re.Pattern[str] = re.compile(r"^\d+x\d+$")) -> str:
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError("invalid value: <width>x<height> expected.")
    return arg_value


def control_type(arg_value: str) -> list[str]:
    if "=" in arg_value:
        return arg_value.split("=")
    else:
        raise argparse.ArgumentTypeError(f"invalid control: Missing value: {arg_value}")


def orientation_type(arg_value: str) -> int:
    if arg_value in option_to_exif_orientation:
        return option_to_exif_orientation[arg_value]
    else:
        raise argparse.ArgumentTypeError(
            f"invalid value: unknown orientation {arg_value}."
        )


def parse_autofocus(arg_value: str) -> libcamera.controls.AfModeEnum:
    if arg_value == "manual":
        return libcamera.controls.AfModeEnum.Manual
    elif arg_value == "continuous":
        return libcamera.controls.AfModeEnum.Continuous
    else:
        raise argparse.ArgumentTypeError(
            "invalid value: manual or continuous expected."
        )


def parse_autofocus_speed(arg_value: str) -> libcamera.controls.AfSpeedEnum:
    if arg_value == "normal":
        return libcamera.controls.AfSpeedEnum.Normal
    elif arg_value == "fast":
        return libcamera.controls.AfSpeedEnum.Fast
    else:
        raise argparse.ArgumentTypeError("invalid value: normal or fast expected.")


def split_resolution(res: str) -> tuple[int, int]:
    parts = res.lower().split("x")
    w = int(parts[0])
    h = int(parts[1])
    return w, h


def parse_quality(quality):
    try:
        return Quality[quality.upper()]
    except:
        raise argparse.ArgumentTypeError(f"Invalid quality choice: {quality}")


# endregion args parsers


# region cli args


def get_args(args: list[str]) -> argparse.Namespace:
    """Parse arguments passed in from shell."""
    return get_parser().parse_args(args)


def get_parser() -> argparse.ArgumentParser:
    """Return ArgumentParser for hello cli."""
    parser = argparse.ArgumentParser(
        allow_abbrev=True,
        prog="spyglass",
        description="Start a webserver for Picamera2 videostreams.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-b",
        "--bindaddress",
        type=str,
        default="0.0.0.0",
        help="Bind to address for incoming " "connections",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8080,
        help="Bind to port for incoming connections",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        type=resolution_type,
        default="640x480",
        help="Resolution of the images width x height. Maximum is 1920x1920.",
    )
    parser.add_argument(
        "-f", "--fps", type=int, default=15, help="Frames per second to capture"
    )
    parser.add_argument(
        "-st",
        "--stream-url",
        "--stream_url",
        type=str,
        default="/?action=stream",
        help="Sets the URL for the MJPG stream",
    )
    parser.add_argument(
        "-sn",
        "--snapshot-url",
        "--snapshot_url",
        type=str,
        default="/?action=snapshot",
        help="Sets the URL for snapshots (single frame of stream)",
    )
    parser.add_argument(
        "-sw",
        "--use-sw-encoding",
        "--use_sw_jpg_encoding",
        action="store_true",
        help="Use software encoding for JPEG and MJPG (Disables WebRTC)",
    )
    parser.add_argument(
        "-w",
        "--webrtc-url",
        "--webrtc_url",
        type=str,
        default="/webrtc",
        help="Sets the URL for the WebRTC stream",
    )
    parser.add_argument(
        "--force-webrtc",
        action=argparse.BooleanOptionalAction,
        help="Force WebRTC streaming to start",
    )
    parser.add_argument(
        "--disable_webrtc",
        action="store_true",
        help="DEPRECATED",
    )
    parser.add_argument(
        "-af",
        "--autofocus",
        type=str,
        default="continuous",
        choices=["manual", "continuous"],
        help="Autofocus mode",
    )
    parser.add_argument(
        "-l",
        "--lensposition",
        type=float,
        default=0.0,
        help="Set focal distance. 0 for infinite focus, 0.5 for approximate 50cm. "
        "Only used with Autofocus manual",
    )
    parser.add_argument(
        "-s",
        "--autofocusspeed",
        type=str,
        default="normal",
        choices=["normal", "fast"],
        help="Autofocus speed. Only used with Autofocus continuous",
    )
    parser.add_argument(
        "-ud",
        "--upsidedown",
        action="store_true",
        help="Rotate the image by 180° (sensor level)",
    )
    parser.add_argument(
        "-fh",
        "--flip-horizontal",
        "--flip_horizontal",
        action="store_true",
        help="Mirror the image horizontally (sensor level)",
    )
    parser.add_argument(
        "-fv",
        "--flip-vertical",
        "--flip_vertical",
        action="store_true",
        help="Mirror the image vertically (sensor level)",
    )
    parser.add_argument(
        "-or",
        "--orientation-exif",
        "--orientation_exif",
        type=orientation_type,
        default="h",
        help="Set the image orientation using an EXIF header. This does not work with WebRTC:\n"
        "  h      - Horizontal (normal)\n"
        "  mh     - Mirror horizontal\n"
        "  r180   - Rotate 180\n"
        "  mv     - Mirror vertical\n"
        "  mhr270 - Mirror horizontal and rotate 270 CW\n"
        "  r90    - Rotate 90 CW\n"
        "  mhr90  - Mirror horizontal and rotate 90 CW\n"
        "  r270   - Rotate 270 CW",
    )
    parser.add_argument(
        "-c",
        "--controls",
        default=[],
        type=control_type,
        action="extend",
        nargs="*",
        help="Define camera controls to start with spyglass. "
        "Can be used multiple times.\n"
        "Format: <control>=<value>",
    )
    parser.add_argument(
        "-cs",
        "--controls-string",
        default="",
        type=str,
        help="Define camera controls to start with spyglass. "
        "Input as a long string.\n"
        "Format: <control1>=<value1> <control2>=<value2>",
    )
    parser.add_argument(
        "-tf",
        "--tuning-filter",
        "--tuning_filter",
        type=str,
        default=None,
        nargs="?",
        const="",
        help="Set a tuning filter file name.",
    )
    parser.add_argument(
        "-tfd",
        "--tuning-filter-dir",
        "--tuning_filter_dir",
        type=str,
        default=None,
        nargs="?",
        const="",
        help="Set the directory to look for tuning filters.",
    )
    parser.add_argument(
        "--list-controls",
        action="store_true",
        help="List available camera controls and exits.",
    )
    parser.add_argument(
        "--mjpeg-linger-seconds",
        type=int,
        default=-1,
        help="How long the MJPEG encoder (and the camera, when no other "
        "encoder is active) keeps running after the last consumer "
        "disconnects. Use 0 or a small positive value to free encoder and "
        "camera resources while idle, reducing CPU use at the cost of "
        "cold-start latency on the next /snapshot or /stream.\n"
        "  -1 (default) keeps the encoder running once started; spyglass "
        "pre-warms it at startup. Preserves the legacy 'always on' "
        "behavior and the lowest /snapshot latency (e.g. for timelapse "
        "use cases).\n"
        "   0 stops the encoder immediately when the last consumer "
        "disconnects. Lowest idle CPU.\n"
        " > 0 stops the encoder N seconds after the last consumer "
        "disconnects; a fresh request within the window cancels the stop. "
        "Bridges brief reconnects without paying cold-start latency on "
        "each one.",
    )
    parser.add_argument(
        "--webrtc-linger-seconds",
        type=int,
        default=5,
        help="How long the WebRTC (H264) encoder (and the camera, when no "
        "other encoder is active) keeps running after the last peer "
        "disconnects. Use 0 or a small positive value to free encoder and "
        "camera resources while idle, reducing CPU use at the cost of "
        "cold-start latency on the next peer connection.\n"
        "  -1 keeps the encoder running once started; spyglass pre-warms "
        "it at startup.\n"
        "   0 stops the encoder immediately when the last peer "
        "disconnects. Lowest idle CPU; every new peer pays cold-start "
        "latency.\n"
        " > 0 (default: 5) stops the encoder N seconds after the last "
        "peer disconnects; a fresh connection within the window cancels "
        "the stop. Bridges brief reconnects without paying cold-start "
        "latency on each one.",
    )
    parser.add_argument(
        "--mjpg-quality",
        type=parse_quality,
        choices=list(Quality),
        default=None,
        help="Sets the quality for the MJPG stream. Higher quality means less artifacts but higher CPU usage and network bandwidth.",
    )
    parser.add_argument(
        "--h264-quality",
        type=parse_quality,
        choices=list(Quality),
        default=None,
        help="Sets the quality for the WebRTC stream. Higher quality means less artifacts but higher CPU usage and network bandwidth.",
    )
    camera_group = parser.add_mutually_exclusive_group()
    camera_group.add_argument(
        "-n",
        "--camera-num",
        "--camera_num",
        type=int,
        default=0,
        help="Camera number to be used (Works with --list-controls)",
    )
    camera_group.add_argument(
        "-d",
        "--device-path",
        "--device_path",
        type=str,
        help="Camera device path to be used (Works with --list-controls)",
    )
    return parser


# endregion cli args
