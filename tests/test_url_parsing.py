import pytest


@pytest.mark.parametrize(
    "expected_url, incoming_url, expected_output",
    [
        ("/?a=b", "/?a=b", True),
        ("/?a=b", "/?b=a", True),
        ("/?a=b", "/?a=b&", True),
        ("/?a=b", "/?b=c&d=e", True),
        ("/?a=b", "/?a=b&c=d", True),
        ("/?a=b", "/?c=d&a=b", True),
        ("/?a=b&c=d", "/?a=b", True),
        ("/?a=b&c=d", "/?a=b&c=d", True),
        ("/?a=b&c=d", "/?c=d&a=b", True),
        ("/?a=b&c=d", "/?d=e&a=b", True),
        ("/?a=b", "/a?a=b", False),
        ("/?a=b", "/a?b=a", False),
        ("/?a=b", "/a?b=c&d=e", False),
        ("/?a=b&c=d", "/a?a=b", False),
        ("/?a=b&c=d", "/a?a=b&c=d", False),
        ("/?a=b&c=d", "/a?c=d&a=b", False),
        ("/a", "/a", True),
        ("/a", "/b", False),
        ("/a", "/a?b=c", True),
        ("/a", "/a/?b=c", True),
        ("/a", "/b/?b=c", False),
        ("/a", "/?a=b", False),
        ("/a?a=b", "/a?a=b", True),
        ("/a?a=b", "/a?b=a", True),
        ("/a?a=b", "/a?b=c&d=e", True),
        ("/a?a=b&c=d", "/a?a=b", True),
        ("/a?a=b&c=d", "/a?a=b&c=d", True),
        ("/a?a=b&c=d", "/a?c=d&a=b", True),
        ("/a?a=b", "/b?a=b", False),
        ("/a?a=b", "/b?b=a", False),
        ("/a?a=b", "/b?b=c&d=e", False),
        ("/a?a=b&c=d", "/b?a=b", False),
        ("/a?a=b&c=d", "/b?a=b&c=d", False),
        ("/a?a=b&c=d", "/b?c=d&a=b", False),
    ],
)
def test_check_paths_match(expected_url, incoming_url, expected_output):
    from spyglass.url_parsing import check_paths_match

    match_value = check_paths_match(expected_url, incoming_url)
    assert match_value == expected_output


@pytest.mark.parametrize(
    "expected_url, incoming_url, expected_output",
    [
        ("/?a=b", "/?a=b", True),
        ("/?a=b", "/?b=a", False),
        ("/?a=b", "/?a=b&", True),
        ("/?a=b", "/?b=c&d=e", False),
        ("/?a=b", "/?a=b&c=d", True),
        ("/?a=b", "/?c=d&a=b", True),
        ("/?a=b&c=d", "/?a=b", False),
        ("/?a=b&c=d", "/?a=b&c=d", True),
        ("/?a=b&c=d", "/?c=d&a=b", True),
        ("/?a=b&c=d", "/?d=e&a=b", False),
        ("/?a=b", "/a?a=b", True),
        ("/?a=b", "/a?b=a", False),
        ("/?a=b", "/a?b=c&d=e", False),
        ("/?a=b&c=d", "/a?a=b", False),
        ("/?a=b&c=d", "/a?a=b&c=d", True),
        ("/?a=b&c=d", "/a?c=d&a=b", True),
        ("/a", "/a", True),
        ("/a", "/b", True),
        ("/a", "/a?b=c", True),
        ("/a", "/a/?b=c", True),
        ("/a", "/b/?b=c", True),
        ("/a", "/?a=b", True),
        ("/a?a=b", "/a?a=b", True),
        ("/a?a=b", "/a?b=a", False),
        ("/a?a=b", "/a?b=c&d=e", False),
        ("/a?a=b&c=d", "/a?a=b", False),
        ("/a?a=b&c=d", "/a?a=b&c=d", True),
        ("/a?a=b&c=d", "/a?c=d&a=b", True),
        ("/a?a=b", "/b?a=b", True),
        ("/a?a=b", "/b?b=a", False),
        ("/a?a=b", "/b?b=c&d=e", False),
        ("/a?a=b&c=d", "/b?a=b", False),
        ("/a?a=b&c=d", "/b?a=b&c=d", True),
        ("/a?a=b&c=d", "/b?c=d&a=b", True),
    ],
)
def test_check_params_match(expected_url, incoming_url, expected_output):
    from spyglass.url_parsing import check_params_match

    match_value = check_params_match(expected_url, incoming_url)
    assert match_value == expected_output


@pytest.mark.parametrize(
    "expected_url, incoming_url, expected_output",
    [
        ("/?a=b", "/?a=b", True),
        ("/?a=b", "/?b=a", False),
        ("/?a=b", "/?a=b&", True),
        ("/?a=b", "/?b=c&d=e", False),
        ("/?a=b", "/?a=b&c=d", True),
        ("/?a=b", "/?c=d&a=b", True),
        ("/?a=b&c=d", "/?a=b", False),
        ("/?a=b&c=d", "/?a=b&c=d", True),
        ("/?a=b&c=d", "/?c=d&a=b", True),
        ("/?a=b&c=d", "/?d=e&a=b", False),
        ("/?a=b", "/a?a=b", False),
        ("/?a=b", "/a?b=a", False),
        ("/?a=b", "/a?b=c&d=e", False),
        ("/?a=b&c=d", "/a?a=b", False),
        ("/?a=b&c=d", "/a?a=b&c=d", False),
        ("/?a=b&c=d", "/a?c=d&a=b", False),
        ("/a", "/a", True),
        ("/a", "/b", False),
        ("/a", "/a?b=c", True),
        ("/a", "/a/?b=c", True),
        ("/a", "/b/?b=c", False),
        ("/a", "/?a=b", False),
        ("/a?a=b", "/a?a=b", True),
        ("/a?a=b", "/a?b=a", False),
        ("/a?a=b", "/a?b=c&d=e", False),
        ("/a?a=b&c=d", "/a?a=b", False),
        ("/a?a=b&c=d", "/a?a=b&c=d", True),
        ("/a?a=b&c=d", "/a?c=d&a=b", True),
        ("/a?a=b", "/b?a=b", False),
        ("/a?a=b", "/b?b=a", False),
        ("/a?a=b", "/b?b=c&d=e", False),
        ("/a?a=b&c=d", "/b?a=b", False),
        ("/a?a=b&c=d", "/b?a=b&c=d", False),
        ("/a?a=b&c=d", "/b?c=d&a=b", False),
    ],
)
def test_check_urls_match(expected_url, incoming_url, expected_output):
    from spyglass.url_parsing import check_urls_match

    match_value = check_urls_match(expected_url, incoming_url)
    assert match_value == expected_output
