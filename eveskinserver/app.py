import csv
import os
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


DEFAULT_SKIN_ICON = "102"  # SKIN icon to use if icon file is missing

app = Flask(__name__)

current_folder = os.path.dirname(os.path.realpath(__file__))
generated_icons_folder = tempfile.mkdtemp()
app.logger.info("Storing generated icons in: %s", generated_icons_folder)


def load_type_2_icon() -> dict:
    """returns generated mapping from type ID to icon ID"""

    app.logger.info("Building type to icon ID mappings...")
    with open(f"{current_folder}/ccp_data/sde/skinLicense.csv", mode="r") as csv_file:
        skin_licenses = list(csv.reader(csv_file, delimiter=","))

    type_2_skin = {row[0]: row[2] for row in skin_licenses}

    with open(f"{current_folder}/ccp_data/sde/skins.csv", mode="r") as csv_file:
        skins = list(csv.reader(csv_file, delimiter=","))

    skin_2_icon = {row[0]: row[2] for row in skins}
    return {
        type_id: skin_2_icon.get(skin_id) for type_id, skin_id in type_2_skin.items()
    }


type_to_icon_mapping = load_type_2_icon()


@app.route("/favicon.ico")
def favicon():
    return send_file(f"{current_folder}/static/icon.png", mimetype="image/png")


@app.route("/", methods=["GET"])
def index():
    """Homepage"""
    return render_template("index.html", app_name=__title__, version=__version__)


@app.route("/skin/<type_id>/icon", methods=["GET"])
def api(type_id):
    """Handles all API calls for this server"""
    try:
        size = int(request.args.get("size"))
    except (ValueError, TypeError):
        app.logger.warning("Invalid size provided. Falling back to 64 as default.")
        size = None

    if not size or size < 32 or size > 1024 or (size & (size - 1) != 0):
        size = 64

    icon_id = type_to_icon_mapping.get(type_id)
    if not icon_id:
        abort(404)

    icon_name = str(icon_id)
    output_filepath = icon_sized_filepath(icon_name, size)
    if not os.path.isfile(output_filepath):
        output_filepath = generate_sized_icon(icon_name, size)

    response = make_response(send_file(output_filepath, mimetype="image/png"))
    _, filename = os.path.split(output_filepath)
    response.headers["x-suggested-filename"] = filename
    return response


def icon_base_filepath(icon_name: str) -> str:
    return f"{current_folder}/ccp_data/icons/{icon_name}.png"


def icon_sized_filepath(icon_name: str, size: int) -> str:
    return f"{generated_icons_folder}/{icon_name}_{size}.png"


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
        icon_name = DEFAULT_SKIN_ICON
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
