from http import HTTPStatus
from spyglass.url_parsing import get_url_params
from spyglass.camera_options import parse_dictionary_to_html_page, process_controls

# Used for type hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from spyglass.server.http_server import StreamingHandler

def do_GET(handler: 'StreamingHandler'):
    parsed_controls = get_url_params(handler.path)
    processed_controls = process_controls(handler.picam2, parsed_controls)
    handler.picam2.set_controls(processed_controls)
    content = parse_dictionary_to_html_page(handler.picam2, parsed_controls, processed_controls).encode('utf-8')
    handler.send_response(HTTPStatus.OK)
    handler.send_header('Content-Type', 'text/html')
    handler.send_header('Content-Length', len(content))
    handler.end_headers()
    handler.wfile.write(content)
