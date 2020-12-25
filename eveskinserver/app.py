import csv
import tempfile
import os

from flask import Flask, send_file, request, render_template, make_response, abort

from PIL import Image

app = Flask(__name__)


current_path = os.path.dirname(os.path.realpath(__file__))

generated_icons_path = tempfile.mkdtemp()
print(f"Storing generated icons in: {generated_icons_path}")


def load_type_2_icon() -> dict:
    """returns generated mapping from type ID to icon ID"""

    print("Building type to icon ID mappings...")
    with open(f"{current_path}/ccp_data/sde/skinLicense.csv", mode="r") as csv_file:
        skin_licenses = list(csv.reader(csv_file, delimiter=","))

    type_2_skin = {row[0]: row[2] for row in skin_licenses}

    with open(f"{current_path}/ccp_data/sde/skins.csv", mode="r") as csv_file:
        skins = list(csv.reader(csv_file, delimiter=","))

    skin_2_icon = {row[0]: row[2] for row in skins}
    return {
        type_id: skin_2_icon.get(skin_id) for type_id, skin_id in type_2_skin.items()
    }


type_to_icon_mapping = load_type_2_icon()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/skin/<type_id>/icon", methods=["GET"])
def api(type_id):
    try:
        size = int(request.args.get("size"))
    except TypeError:
        size = None

    if not size or size < 32 or size > 1024 or (size & (size - 1) != 0):
        size = 64

    icon_id = type_to_icon_mapping.get(type_id)
    if not icon_id:
        abort(404)

    icon_name = str(icon_id)
    output_filename = icon_sized_filename(icon_name, size)
    if not os.path.isfile(output_filename):
        generate_sized_icon(icon_name, size)

    response = make_response(send_file(output_filename, mimetype="image/png"))
    _, filename = os.path.split(output_filename)
    response.headers["x-suggested-filename"] = filename
    return response


def icon_base_filename(icon_name: str) -> str:
    return f"{current_path}/ccp_data/icons/{icon_name}.png"


def icon_sized_filename(icon_name: str, size: int) -> str:
    return f"{generated_icons_path}/{icon_name}_{size}.png"


def generate_sized_icon(icon_name: str, size: int):
    try:
        img = Image.open(icon_base_filename(icon_name))
    except IOError:
        img = Image.open(icon_base_filename("default"))
    else:
        w_percent = size / float(img.size[0])
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((size, h_size), Image.ANTIALIAS)
        img.save(icon_sized_filename(icon_name, size))


if __name__ == "__main__":
    app.run(debug=True, port=5000)  # run app in debug mode on port 5000
