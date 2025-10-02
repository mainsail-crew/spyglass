# Spyglass

> **Please note that we cannot support 32 bit systems. For more information please
have a look at [this comment](https://github.com/mryel00/spyglass/issues/116#issuecomment-3361184578).**

A simple mjpeg server for the python module [Picamera2](https://github.com/raspberrypi/picamera2).

With Spyglass you are able to stream videos from a camera that is supported by [libcamera](http://libcamera.org) like
the [Raspberry Pi Camera Modules](https://www.raspberrypi.com/documentation/accessories/camera.html).

Current version: 0.17.0

## Overview

-   [Quickstart](#quick-start)
-   [Installation](#installation)
-   [CLI arguments](#cli-arguments)
-   [FAQ](#faq)
    -   [How can I add CLI arguments to my `spyglass.conf`?](#how-can-i-add-cli-arguments-to-my-spyglassconf)
    -   [How to use resolutions higher than maximum resolution?](#how-to-use-resolutions-higher-than-maximum-resolution)
    -   [Why is the CPU load on my Pi5 so high?](#why-is-the-cpu-load-on-my-pi5-so-high)
    -   [How can I rotate the image of my stream?](#how-can-i-rotate-the-image-of-my-stream)
    -   [How to apply tuning filter?](#how-to-apply-tuning-filter)
    -   [How to use the WebRTC endpoint?](#how-to-use-the-webrtc-endpoint)
    -   [How to use Spyglass with Mainsail?](#how-to-use-spyglass-with-mainsail)
    -   [How to use the controls endpoint?](#how-to-use-the-controls-endpoint)
    -   [How to start developing?](#how-to-start-developing)


## Quick Start

The server can be started with

```bash
./run.py
```

This will start the server with the following default configuration:

-   Address the server binds to: 0.0.0.0
-   Port: 8080
-   Resolution: 640x480
-   Framerate: 15 FPS
-   Stream URL: /stream
-   Snapshot URL: /snapshot
-   WebRTC URL: /webrtc
-   Controls URL: /controls

The stream can then be accessed at `http://<IP of the server>:8080/stream`.\
You might need to install dependencies, refer to the [installation section](#installation) below.

## Installation

Run following commands to install and run Spyglass as a service:

```bash
cd ~
sudo apt update
sudo apt install python3-libcamera python3-kms++ python3-picamera2 git -y
git clone https://github.com/mryel00/spyglass
cd ~/spyglass
make install
```

This will ask you for your `sudo` password.\
After install is done, please reboot to ensure service starts properly

To uninstall the service simply use

```bash
cd ~/spyglass
make uninstall
```

### Use Moonraker Update Manager

To be able to use Moonraker update manager, add the following lines to your `moonraker.conf`:

```conf
[update_manager spyglass]
type: git_repo
path: ~/spyglass
origin: https://github.com/mryel00/spyglass.git
primary_branch: main
virtualenv: .venv
requirements: requirements.txt
system_dependencies: resources/system-dependencies.json
managed_services: spyglass
```
> Make sure moonraker.asvc contains `spyglass` in the list: `cat ~/printer_data/moonraker.asvc | grep spyglass`.
> If it is not there execute `make upgrade-moonraker` or add it manually

### Configuration

After installation you should find a configuration file in `~/printer_data/config/spyglass.conf`.\
Please see [spyglass.conf](resources/spyglass.conf) for the default config file and [CLI arguments](#cli-arguments) for
all available options.

### Restart the service

To restart the service use `systemctl`:

```bash
sudo systemctl restart spyglass
```

## CLI arguments

On startup the following arguments are supported:

| Argument                       | Description                                                                                                                        | Default      |
|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------|--------------|
| `-b`, `--bindaddress`          | Address where the server will listen for incoming connections.                                                                     | `0.0.0.0`    |
| `-p`, `--port`                 | Port where the server will listen for incoming connections.                                                                        | `8080`       |
| `-r`, `--resolution`           | Resolution of the captured frames. This argument expects the format \<width\>x\<height\>.                                          | `640x480`    |
| `-f`, `--fps`                  | Framerate in frames per second (FPS).                                                                                              | `15`         |
| `-st`, `--stream_url`          | Set the URL for the mjpeg stream.                                                                                                  | `/stream`    |
| `-sn`, `--snapshot_url`        | Set the URL for snapshots (single frame of stream).                                                                                | `/snapshot`  |
| `-w`, `--webrtc_url`           | Set  the URL for WebRTC (H264 compressed stream).                                                                                  | `/webrtc`    |
| `-af`, `--autofocus`           | Autofocus mode. Supported modes: `manual`, `continuous`.                                                                           | `continuous` |
| `-l`, `--lensposition`         | Set focal distance. 0 for infinite focus, 0.5 for approximate 50cm. Only used with Autofocus manual.                               | `0.0`        |
| `-s`, `--autofocusspeed`       | Autofocus speed. Supported values: `normal`, `fast`. Only used with Autofocus continuous.                                          | `normal`     |
| `-ud`, `--upsidedown`          | Rotate the image by 180° (see [below](#image-orientation)).                                                                        |              |
| `-fh`, `--flip_horizontal`     | Mirror the image horizontally (see [below](#image-orientation)).                                                                   |              |
| `-fv`, `--flip_vertical`       | Mirror the image vertically (see [below](#image-orientation)).                                                                     |              |
| `-or`, `--orientation_exif`    | Set the image orientation using an EXIF header (see [below](#image-orientation)).                                                  |              |
| `-c`, `--controls`             | Define camera controls to start spyglass with. Can be used multiple times. This argument expects the format \<control\>=\<value\>. |              |
| `-tf`, `--tuning_filter`       | Set a tuning filter file name.                                                                                                     |              |
| `-tfd`, `--tuning_filter_dir`  | Set the directory to look for tuning filters.                                                                                      |              |
| `-n`, `--camera_num`           | Camera number to be used. All cameras with their number can be shown with `libcamera-hello`.                                       | `0`          |
| `-sw`, `--use_sw_jpg_encoding` | Use software encoding for JPEG and MJPG (recommended on Pi5).                                                                      |              |
| `--disable_webrtc`             | Disable WebRTC encoding (recommended on Pi5).                                                                                      |              |
| `--list-controls`              | List all available libcamera controls onto the console. Those can be used with `--controls`.                                       |              |


## FAQ

### How can I add CLI arguments to my `spyglass.conf`?

All supported CLI arguments are already inside the [defaul config](resources/spyglass.conf).
If we add new arguments we will add them there, so please refer to it, if you want to use a new argument.

In the following sections we will only refer to the CLI arguments but you can use the `spyglass.conf` for all these too.

### How to use resolutions higher than maximum resolution?

Please note that the maximum recommended resolution is 1920x1080 (16:9).

The absolute maximum resolution is 1920x1920. If you choose a higher resolution spyglass may stop with
`Maximum supported resolution is 1920x1920`. This is limited by the hardware (HW) encoder of the Pis.\
You can disable this limit with `--use_sw_jpg_encoding` and `--disable_webrtc`, or the respective config in
`spyglass.conf`, but it will take way more CPU resources to run the stream and WebRTC won't work anymore.
Only a Pi5 you don't need to add `--disable_webrtc`, for further information please refer to
[Pi5 recommendations](#pi5-recommendations).

### Why is the CPU load on my Pi5 so high?

The Pi5 is the newest generation of Raspberry Pi SBCs but not all new things come with improvements.
The Raspberry Pi foundation decided to remove the hardware (HW) encoders from the Pi5.
This results in overall higher CPU usage on a Pi5 compared to previous generations.

The following sections should only be followed on a Pi5.\
WebRTC is also a big toll on your CPU. Therefore you should use `--disable_webrtc`.\
To reduce the CPU usage further you should add `--use_sw_jpg_encoding` to make sure to use the optimized software (SW)
encoder, instead of the HW encoder falling back to an unoptimized SW encoder.

### How can I rotate the image of my stream?

There are two ways to change the image orientation.

To use the ability of picamera2 to transform the image you can use the following options when starting spyglass:
 * `-ud` or `--upsidedown` - Rotate the image by 180°
 * `-fh` or `--flip_horizontal` - Mirror the image horizontally
 * `-fv` or `--flip_vertical` - Mirror the image vertically

This will work with all endpoints Spyglass offers.

Alternatively you can create an EXIF header to modify the image orientation. Most modern browsers should respect
the exif header. This will only work for the MJPG and JPEG endpoints.

Use the `-or` or `--orientation_exif` option and choose from one of the following orientations
 * `h` - Horizontal (normal)
 * `mh` - Mirror horizontal
 * `r180` - Rotate 180
 * `mv` - Mirror vertical
 * `mhr270` - Mirror horizontal and rotate 270 CW
 * `r90` - Rotate 90 CW
 * `mhr90` - Mirror horizontal and rotate 90 CW
 * `r270` - Rotate 270 CW

For example to rotate the image 90 degree clockwise you would start spyglass the following way:
```bash
./run.py -or r90
```

### How to apply tuning filter?
Tuning filters are used to normalize or modify the camera image output, for example, using an NoIR camera can lead to a
pink color, whether applying a filter to it you could remove its tone pink. More information here:
https://github.com/raspberrypi/picamera2/blob/main/examples/tuning_file.py


Predefined filters can be found at one of the picamera2 directories:
- `~/libcamera/src/ipa/rpi/vc4/data`
- `/usr/local/share/libcamera/ipa/rpi/vc4`
- `/usr/share/libcamera/ipa/rpi/vc4`
- `/usr/share/libcamera/ipa/raspberrypi`

You can use all the files present in there in our config, e.g.: `--tuning_filter=ov5647_noir.json`

You can also define your own directory for filters using the `--tuning_filter_dir` argument.

### How to use the WebRTC endpoint?

Spyglass does not deliver a streaming client for WebRTC but only the endpoint. We are using the same WebRTC protocol as
[MediaMTX](https://github.com/bluenviron/mediamtx). Therefore you need to use e.g. Mainsail or any other client capable
of using the MediaMTX stream.

### How to use Spyglass with Mainsail?

> Note: In the following section we assume default settings.

If you want to use Spyglass as a webcam source for [Mainsail](https://github.com/mainsail-crew/Mainsail) add a webcam
with the following configuration:

-   URL Stream: `/webcam/stream`
-   URL Snapshot: `/webcam/snapshot`
-   Service: `MJPEG-Streamer`

Alternatively you can use WebRTC. This will take less network bandwidth and might help to fix low FPS:

-   URL Stream: `/webcam/webrtc`
-   URL Snapshot: `/webcam/snapshot`
-   Service: `WebRTC (MediaMTX)`

WebRTC needs [aiortc](https://github.com/aiortc/aiortc) installed. This gets automatically installed with `make install`
for further instructions, please see the [install](#installation) chapter below.

### How to use the controls endpoint?

For the control endpoint please refer to [this](docs/camera-controls.md)

### How to start developing?

If you want to setup your environment for development perform the following steps:

Setup your Python virtual environment:
```bash
python -m venv .venv                  # Create a new virtual environment
. .venv/bin/activate                  # Activate virtual environment
python -m pip install --upgrade pip   # Upgrade PIP to the current version
pip install -r requirements.txt       # Install application dependencies
pip install -r requirements-test.txt  # Install test dependencies
pip install -r requirements-dev.txt   # Install development dependencies
```

The project uses [commitizen](https://github.com/commitizen-tools/commitizen) to check commit messages to comply with
[Conventional Commits](http://conventionalcommits.org). When installing the development dependencies git-hooks will be
set up to check commit messages pre commit.
