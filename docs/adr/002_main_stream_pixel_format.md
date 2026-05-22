# 002 - Main Stream Pixel Format for CSI Cameras

## Date

2026-05-31

## Status

Decision

## Category

Performance

## Authors

@antoinecellerier

## References

[picamera2 V4L2 encoder source](https://github.com/raspberrypi/picamera2/blob/main/picamera2/encoders/v4l2_encoder.py)

## Context

`picamera2.create_video_configuration()` defaults the main stream to `XBGR8888`
(32 bits/pixel). Both the V4L2 hardware encoders (`MJPEGEncoder`,
`H264Encoder`) and the `JpegEncoder` software fallback accept `YUV420`
(12 bits/pixel) as a native input. Forcing `YUV420` upstream of the encoders
skips an implicit colour-space conversion and reduces DMA bandwidth by ~2.7×.

## Options

1. Keep the picamera2 default (`XBGR8888`).
2. Request `YUV420` for the main stream, falling back to the picamera2 default
   when the camera does not advertise it.

## Decision

We request `YUV420` for the main stream when libcamera reports it as supported,
selected from a preference-ordered list of encoder-compatible formats with
`YUV420` first. If none are supported, we omit `format` from the config and
defer to the picamera2 default.

## Consequences

* Measured CPU on a Pi 4B with Camera Module 3 at 1920×1080 @ 30 fps drops by
  ~28–39 % (idle and live WebRTC respectively) versus the `XBGR8888` default.
* No expected image-quality impact: JPEG and H.264 both encode in YUV
  internally, so this change moves the colour-space conversion earlier in the
  pipeline rather than introducing a new one.
