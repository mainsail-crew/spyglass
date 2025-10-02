def create_exif_header(orientation: int):
    if orientation <= 0:
        return None

    return b"".join(
        [
            b"\xff\xd8",  # Start of Image (SOI) marker
            b"\xff\xe1",  # APP1 marker
            b"\x00\x62",  # Length of APP 1 segment (98 bytes)
            b"\x45\x78\x69\x66",  # EXIF identifier ("Exif" in ASCII)
            b"\x00\x00",  # Padding bytes
            # TIFF header (with big-endian indicator)
            b"\x4d\x4d",  # Big endian
            b"\x00\x2a",  # TIFF magic number
            b"\x00\x00\x00\x08",  # Offset to first IFD (8 bytes)
            # Image File Directory (IFD)
            b"\x00\x05",  # Number of entries in the IFD (5)
            # v-- Orientation tag (tag number = 0x0112, type = USHORT, count = 1)
            b"\x01\x12",
            b"\x00\x03",
            b"\x00\x00\x00\x01",
            b"\x00",
            orientation.to_bytes(1, "big"),
            b"\x00\x00",  # Tag data
            # v-- XResolution tag (tag number = 0x011A, type = UNSIGNED RATIONAL, count = 1)
            b"\x01\x1a",
            b"\x00\x05",
            b"\x00\x00\x00\x01",
            b"\x00\x00\x00\x4a",  # Tag data (address)
            # v-- YResolution tag (tag number = 0x011B, type = UNSIGNED RATIONAL, count = 1)
            b"\x01\x1b",
            b"\x00\x05",
            b"\x00\x00\x00\x01",
            b"\x00\x00\x00\x52",  # Tag data (address)
            # v-- ResolutionUnit tag (tag number = 0x0128, type = USHORT, count = 1)
            b"\x01\x28",
            b"\x00\x03",
            b"\x00\x00\x00\x01",
            b"\x00\x02\x00\x00",  # 2 - Inch
            # v-- YCbCrPositioning tag (tag number = 0x0213, type = USHORT, count = 1)
            b"\x02\x13",
            b"\x00\x03",
            b"\x00\x00\x00\x01",
            b"\x00\x01\x00\x00",  # center of pixel array
            b"\x00\x00\x00\x00",  # Offset to next IFD 0
            b"\x00\x00\x00\x48\x00\x00\x00\x01",  # XResolution value
            b"\x00\x00\x00\x48\x00\x00\x00\x01",  # YResolution value
        ]
    )


option_to_exif_orientation = {
    "h": 1,
    "mh": 2,
    "r180": 3,
    "mv": 4,
    "mhr270": 5,
    "r90": 6,
    "mhr90": 7,
    "r270": 8,
}
