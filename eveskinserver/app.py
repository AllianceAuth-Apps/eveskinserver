import csv
from pathlib import Path
import tempfile

from flask import (
    Flask,
    send_file,
    request,
    render_template,
    make_response,
    abort,
)
from PIL import Image

from eveskinserver import __version__, __title__


DEFAULT_SIZE = 64
MINIMUM_SIZE = 32
MAXIMUM_SIZE = 1024
DEFAULT_ICON_NAME = "102"  # SKIN icon to use if icon file is missing

app = Flask(__name__)

current_folder = Path(__file__).parent
generated_icons_folder = Path(tempfile.mkdtemp())
app.logger.info("Storing generated icons in: %s", generated_icons_folder)
sde_folder = current_folder / "ccp_data" / "sde"
icons_folder = current_folder / "ccp_data" / "icons"
static_folder = current_folder / "static"
templates_folder = current_folder / "templates"


def load_type_2_icon() -> dict:
    """returns generated mapping from type ID to icon ID"""
    app.logger.info("Building type to icon ID mappings...")
    with open(sde_folder / "skinLicense.csv", mode="r") as csv_file:
        skin_licenses = list(csv.reader(csv_file, delimiter=","))

    type_2_skin = {row[0]: row[2] for row in skin_licenses}

    with open(sde_folder / "skins.csv", mode="r") as csv_file:
        skins = list(csv.reader(csv_file, delimiter=","))

    skin_2_icon = {row[0]: row[2] for row in skins}
    return {
        type_id: skin_2_icon.get(skin_id) for type_id, skin_id in type_2_skin.items()
    }


type_to_icon_mapping = load_type_2_icon()


@app.route("/favicon.ico")
def favicon():
    return send_file(static_folder / "icon.png", mimetype="image/png")


@app.route("/", methods=["GET"])
def index():
    """Homepage"""
    return render_template(
        "index.html", app_name=__title__, version=__version__, default_size=DEFAULT_SIZE
    )


@app.route("/skin/<type_id>/icon", methods=["GET"])
def api(type_id):
    """Handles all API calls for this server"""
    size = request.args.get("size") if request.args.get("size") else DEFAULT_SIZE
    if size:
        try:
            size = int(size)
        except (ValueError, TypeError):
            size = None

    if (
        not size
        or size < MINIMUM_SIZE
        or size > MAXIMUM_SIZE
        or (size & (size - 1) != 0)
    ):
        app.logger.warning(f"Invalid size '{size}' provided")
        abort(400)

    icon_id = type_to_icon_mapping.get(type_id)
    if not icon_id:
        abort(404)

    icon_name = str(icon_id)
    output_filepath = icon_sized_filepath(icon_name, size)
    if not output_filepath.exists():
        output_filepath = generate_sized_icon(icon_name, size)

    response = make_response(send_file(output_filepath, mimetype="image/png"))
    response.headers["x-suggested-filename"] = output_filepath.name
    return response


def icon_base_filepath(icon_name: str) -> Path:
    return icons_folder / f"{icon_name}.png"


def icon_sized_filepath(icon_name: str, size: int) -> Path:
    return generated_icons_folder / f"{icon_name}_{size}.png"


def generate_sized_icon(icon_name: str, size: int) -> str:
    """generated a sized icon and stores it. Returns the full path to that file"""
    app.logger.info("Generating icon for %s of size %s", icon_name, size)
    try:
        with Image.open(icon_base_filepath(icon_name)) as img:
            img.load()
    except FileNotFoundError:
        app.logger.warning(
            "Could not find icon file for '%s'. Using default instead.", icon_name
        )
        icon_name = DEFAULT_ICON_NAME
        with Image.open(icon_base_filepath(icon_name)) as img:
            img.load()

    w_percent = size / float(img.size[0])
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((size, h_size), Image.ANTIALIAS)
    output_filepath = icon_sized_filepath(icon_name, size)
    img.save(output_filepath)
    return output_filepath


if __name__ == "__main__":
    app.run(debug=True, port=5000)  # run app in debug mode on port 5000
