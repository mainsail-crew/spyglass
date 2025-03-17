# Spyglass

> **Please note that this project is in a very early stage. Use at your own risk. Think about contributing to the project
if you find that something is not working, and you are able to fix it. Every contribution is appreciated.**

A simple mjpeg server for Picamera2.

With Spyglass you are able to stream videos from a camera that is supported by [libcamera](http://libcamera.org) like
the [Raspberry Pi Camera Module 3](https://www.raspberrypi.com/products/camera-module-3/).

Current version: 0.16.3

## Prerequisites

-   Raspberry Pi OS Bullseye
-   [Picamera2](https://github.com/raspberrypi/picamera2) - Already installed on Raspberry Pi OS Bullseye
-   Python 3.8+
-   A camera supported by libcamera and connected to the Raspberry Pi

## Quick Start

The server can be started with

```shell
./run.py
```

This will start the server with the following default configuration:

-   Address the server binds to: 0.0.0.0
-   Port: 8080
-   Resolution: 640x480
-   Framerate: 15fps
-   Stream URL: /stream
-   Snapshot URL: /snapshot

## Configuration

On startup the following arguments are supported:

| Argument                       | Description                                                                                                                        | Default      |
|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------|--------------|
| `-b`, `--bindaddress`          | Address where the server will listen for new incoming connections.                                                                 | `0.0.0.0`    |
| `-p`, `--port`                 | Port where the server will listen for new incoming connections.                                                                    | `8080`       |
| `-r`, `--resolution`           | Resolution of the captured frames. This argument expects the format \<width\>x\<height\>                                           | `640x480`    |
| `-f`, `--fps`                  | Framerate in frames per second (fps).                                                                                              | `15`         |
| `-st`, `--stream_url`          | Sets the URL for the mjpeg stream.                                                                                                 | `/stream`    |
| `-sn`, `--snapshot_url`        | Sets the URL for snapshots (single frame of stream).                                                                               | `/snapshot`  |
| `-w`, `--webrtc_url`           | Sets the URL for WebRTC (H264 compressed stream).                                                                                  | `/webrtc`    |
| `-af`, `--autofocus`           | Autofocus mode. Supported modes: `manual`, `continuous`.                                                                           | `continuous` |
| `-l`, `--lensposition`         | Set focal distance. 0 for infinite focus, 0.5 for approximate 50cm. Only used with Autofocus manual.                               | `0.0`        |
| `-s`, `--autofocusspeed`       | Autofocus speed. Supported values: `normal`, `fast`. Only used with Autofocus continuous                                           | `normal`     |
| `-ud`, `--upsidedown`          | Rotate the image by 180° (see [below](#image-orientation))                                                                         |              |
| `-fh`, `--flip_horizontal`     | Mirror the image horizontally (see [below](#image-orientation))                                                                    |              |
| `-fv`, `--flip_vertical`       | Mirror the image vertically (see [below](#image-orientation))                                                                      |              |
| `-or`, `--orientation_exif`    | Set the image orientation using an EXIF header (see [below](#image-orientation))                                                   |              |
| `-c`, `--controls`             | Define camera controls to start spyglass with. Can be used multiple times. This argument expects the format \<control\>=\<value\>. |              |
| `-tf`, `--tuning_filter`       | Set a tuning filter file name.                                                                                                     |              |
| `-tfd`, `--tuning_filter_dir`  | Set the directory to look for tuning filters.                                                                                      |              |
| `-n`, `--camera_num`           | Camera number to be used. All cameras with their number can be shown with `libcamera-hello`.                                       | `0`          |
| `-sw`, `--use_sw_jpg_encoding` | Use software encoding for JPEG and MJPG (recommended on Pi5).                                                                      |              |
| `--disable_webrtc`             | Disables WebRTC encoding (recommended on Pi5).                                                                                     |              |
| `--list-controls`              | List all available libcamera controls onto the console. Those can be used with `--controls`                                        |              |

Starting the server without any argument is the same as

```shell
./run.py -b 0.0.0.0 -p 8080 -r 640x480 -f 15 -st '/stream' -sn '/snapshot' -af continuous -l 0.0 -s normal -n 0
```

The stream can then be accessed at `http://<IP of the server>:8080/stream`

### Maximum resolution

Please note that the maximum recommended resolution is 1920x1080 (16:9).

The absolute maximum resolution is 1920x1920. If you choose a higher resolution spyglass may crash.

### Image Orientation

There are two ways to change the image orientation.

To use the ability of picamera2 to transform the image you can use the following options when starting spyglass:
 * `-ud` or `--upsidedown` - Rotate the image by 180°
 * `-fh` or `--flip_horizontal` - Mirror the image horizontally
 * `-fv` or `--flip_vertical` - Mirror the image vertically

Alternatively you can create an EXIF header to modify the image orientation. Most modern browsers should respect the
this header.

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
```shell
./run.py -or r90
```

### Tuning filter
Tuning filters are used to normalize or modify the camera image output, for example, using an NoIR camera can lead to a pink color, whether applying a filter to it you could remove its tone pink. More information here: https://github.com/raspberrypi/picamera2/blob/main/examples/tuning_file.py


Predefined filters can be found at one of the picamera2 directories:
- ~/libcamera/src/ipa/rpi/vc4/data
- /usr/local/share/libcamera/ipa/rpi/vc4
- /usr/share/libcamera/ipa/rpi/vc4
- /usr/share/libcamera/ipa/raspberrypi

You can also define your own directory of filter by using parameter `tuning_filter_dir`.

list the files present there and you can use it in our config. eg.: `ov5647_noir.json`


## Using Spyglass with Mainsail

If you want to use Spyglass as a webcam source for [Mainsail]() add a webcam with the following configuration:

-   URL Stream: `/webcam/stream`
-   URL Snapshot: `/webcam/snapshot`
-   Service: `V4L-MJPEG`

Alternatively you can use WebRTC. This will take less network bandwidth and might help to fix low fps:

-   URL Stream: `/webcam/webrtc`
-   URL Snapshot: `/webcam/snapshot`
-   Service: `WebRTC (MediaMTX)`

WebRTC needs [aiortc](https://github.com/aiortc/aiortc) installed. This gets automatically installed with `make install` for further instructions, please see the [install](#install) chapter below.

## Install as application

If you want to install Spyglass globally on your machine you can use `python -m pip install .` to do so.

## Install and run as a service

### Install

Quite simple:

```bash
cd ~
git clone https://github.com/roamingthings/spyglass
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

#### Using Moonraker Update Manager

To be able to use Moonraker update manager, add the following lines to moonraker.conf:

```conf
[update_manager spyglass]
type: git_repo
channel: beta
path: ~/spyglass
origin: https://github.com/roamingthings/spyglass.git
managed_services: spyglass
```
> Make sure moonraker.asvc contains `spyglass` in the list: `cat ~/printer_data/moonraker.asvc | grep spyglass`.
> 
> If not there execute: `make upgrade-moonraker`

### Configuration

You should find a configuration file in `~/printer_data/config/spyglass.conf`.

Please see [spyglass.conf](resources/spyglass.conf) for an example

### Restart the service

To restart the service use `systemctl`:

```shell
sudo systemctl restart spyglass
```

## Start Developing

If you want to setup your environment for development perform the following steps:

Setup your Python virtual environment:
```shell
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

### Problems when Committing to your Branch

 You may get the following error message when you try to push to your branch:
 ```
 fatal: ambiguous argument 'origin/HEAD..HEAD': unknown revision or path not in the working tree.
 Use '--' to separate paths from revisions, like this:
 'git <command> [<revision>...] -- [<file>...]'
 ```
 This error occurs when your HEAD branch is not properly set ([Stack Overflow](https://stackoverflow.com/a/8841024))
 To fix this run the following command:
 ```shell
 git remote set-head origin -a
 ```
