These stub files were generated using `stubgen` (packaged in `mypy`) on a Raspberry Pi using the following commands:
```sh
source .venv/bin/activate
stubgen --include-private -o typings -p picamera2
stubgen --include-private -o typings -p libcamera
```
Small adjustments were made manually to fix issues from auto generation.

Versions:
- `picamera2`: apt package `python3-picamera` version `0.3.36-1`
- `libcamera`: apt package `python3-libcamera` version `0.7.1+rpt20260609-1`
