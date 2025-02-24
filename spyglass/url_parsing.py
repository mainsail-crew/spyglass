from urllib.parse import urlparse, parse_qsl

def check_paths_match(expected_url, incoming_url, match_full_path=True):
    # Assign paths from URL into list
    exp_paths = urlparse(expected_url.strip("/")).path.split("/")
    inc_paths = urlparse(incoming_url.strip("/")).path.split("/")

    # Drop ip/hostname if present in path
    if '.' in exp_paths[0]: exp_paths.pop(0)
    if '.' in inc_paths[0]: inc_paths.pop(0)

    # Filter out empty strings
    # This allows e.g. /stream/?action=stream for /stream?action=stream
    exp_paths = list(filter(None, exp_paths))
    inc_paths = list(filter(None, inc_paths))

    # Determine if match
    if match_full_path and len(exp_paths)==len(inc_paths):
        return all([exp == inc for exp, inc in zip(exp_paths, inc_paths)])
    elif not match_full_path and len(exp_paths)<=len(inc_paths):
        return all([exp == inc for exp, inc in zip(exp_paths, inc_paths)])

    return False

def get_url_params(url):
    # Get URL params
    params = parse_qsl(urlparse(url).query)

    return params

def check_params_match(expected_url, incoming_url):
    # Check URL params
    exp_params = get_url_params(expected_url)
    inc_params = get_url_params(incoming_url)

    # Create list of matching params
    matching_params = set(exp_params) & set(inc_params)

    # Update list order for expected params
    exp_params = set(exp_params)

    return matching_params==exp_params

def check_urls_match(expected_url, incoming_url, match_full_path=True):
    # Check URL paths
    paths_match = check_paths_match(expected_url, incoming_url, match_full_path)

    # Check URL params
    params_match = check_params_match(expected_url, incoming_url)

    return paths_match and params_match
