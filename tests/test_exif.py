import pytest


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        ("h", 1),
        ("mh", 2),
        ("r180", 3),
        ("mv", 4),
        ("mhr270", 5),
        ("r90", 6),
        ("mhr90", 7),
        ("r270", 8),
    ],
)
def test_option_to_exif_orientation_map(input_value, expected_output):
    from spyglass.exif import option_to_exif_orientation

    orientation_value = option_to_exif_orientation[input_value]
    assert orientation_value == expected_output
