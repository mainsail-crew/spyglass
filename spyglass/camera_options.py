import libcamera
import ast

def parse_dictionary_to_html_page(camera, parsed_controls={}, processed_controls={}):
    if not parsed_controls:
        parsed_controls = 'None'
    if not processed_controls:
        processed_controls = 'None'
    html =  """
            <!DOCTYPE html>
            <html lang="en">
            """
    html += f"""
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Camera Settings</title>
                    <style>{get_style()}</style>
                </head>
            """
    html += f"""
                <body>
                    <h1>Available camera options</h1>
                    <h3>Parsed Controls: {parsed_controls}</h3>
                    <h3>Processed Controls: {processed_controls}</h3>
            """
    for control, values in camera.camera_controls.items():
        html += f"""
                    <div class="card-container">
                        <div class="card">
                            <h2>{control}</h2>
                            <div class="card-content">
                            <div class="setting">
                                <span class="label">Min:</span>
                                <span class="value">{values[0]}</span>
                            </div>
                            <div class="setting">
                                <span class="label">Max:</span>
                                <span class="value">{values[1]}</span>
                            </div>
                            <div class="setting">
                                <span class="label">Default:</span>
                                <span class="value">{values[2]}</span>
                            </div>
                            </div>
                        </div>
                    </div>
                """
    html += """
                </body>
            </html>
            """
    return html

def get_style():
    with (open('resources/controls_style.css', 'r')) as f:
        return f.read()

def process_controls(camera, controls: list[tuple[str, str]]) -> dict[str, any]:
    controls_dict_lower = { k.lower(): k for k in camera.camera_controls.keys() }
    if controls == None:
        return {}
    processed_controls = {}
    for key, value in controls:
        key = key.lower().strip()
        if key.lower() in controls_dict_lower.keys():
            value = value.lower().strip()
            k = controls_dict_lower[key]
            v = parse_from_string(value)
            processed_controls[k] = v
    return processed_controls

def parse_from_string(input_string: str) -> any:
    try:
        return ast.literal_eval(input_string)
    except (ValueError, TypeError, SyntaxError):
        pass

    if input_string.lower() in ['true', 'false']:
        return input_string.lower() == 'true'

    return input_string

def get_type_str(obj) -> str:
    return str(type(obj)).split('\'')[1]

def get_libcamera_controls_string(camera_num: str) -> str:
    ctrls_str = ""
    libcam_cm = libcamera.CameraManager.singleton()
    if camera_num > len(libcam_cm.cameras) - 1:
        return ctrls_str
    cam = libcam_cm.cameras[camera_num]

    def rectangle_to_tuple(rectangle):
        return (rectangle.x, rectangle.y, rectangle.width, rectangle.height)

    for k, v in cam.controls.items():
        if isinstance(v.min, libcamera.Rectangle):
            min = rectangle_to_tuple(v.min)
            max = rectangle_to_tuple(v.max)
            default = rectangle_to_tuple(v.default)
        else:
            min = v.min
            max = v.max
            default = v.default

        str_first = f"{k.name} ({get_type_str(min)})"
        str_second = f"min={min} max={max} default={default}"
        str_indent = (30 - len(str_first)) * ' ' + ': '
        ctrls_str += str_first + str_indent + str_second + '\n'

    return ctrls_str.strip()
