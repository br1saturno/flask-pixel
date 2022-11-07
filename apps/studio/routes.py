import os
import io
import warnings
from apps.studio import blueprint
from flask import Flask, flash, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
from apps import db
from PIL import Image

from apps.studio.models import AImages
from apps.studio.forms import StudioForm, styles, color_moods, room_types, color_moods_dict
from apps.studio.util import stability_generation, variation_params, resize_image
from apps.authentication.models import Users
from flask_login import login_required
from flask_login import (
    current_user
)
from jinja2 import TemplateNotFound

app = Flask(__name__)
app.register_blueprint(blueprint)

UPLOAD_FOLDER = 'apps/static/assets/img/bases'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'sdlkfj$%^&fhgfghbdfg'
# sess = Session()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@blueprint.route('/studio', methods=['GET', 'POST'])
@login_required
def generate_image():
    username = None
    scratch = False
    wanted_samples = 1
    if current_user.is_authenticated:
        user_id = current_user.get_id()
        username = str(Users.query.filter_by(id=user_id).first())
    session_id_list = [d[0] for d in db.session.query(AImages.session_id).filter_by(username=username).all()]
    if len(session_id_list) > 0:
        session_id = max(session_id_list) + 1
    else:
        session_id = 1

    # Loads the values for the stability ai function
    if request.method == "POST":
        colors = f""
        for color in color_moods_dict[request.form['color_mood']]:
            if color is color_moods_dict[request.form['color_mood']][0]:
                colors = f"{color} accents"
            else:
                colors += f", {color} accents"
        room_input = ""
        for pair in room_types:
            if request.form['room'] == pair[0]:
                room_input = pair[1].split("-")[1]
        style_input = ""
        for pair in styles:
            if request.form['style'] == pair[0]:
                style_input = pair[1]
        my_prompt = f"A realistic photograph of a{room_input}, {colors}, " \
                    f"{style_input} furniture and {style_input} accesories, 8k, unreal engine, " \
                    f"highly detailed, octane render, sharp, ambient lighting"
        print(my_prompt)
        image_name = f"{username}-{session_id}-{request.form['room']}"
        print(image_name)
        wanted_samples = int(request.form["amountRange"])
        width = int(request.form["widthInput"])
        height = int(request.form["heightInput"])

        # Uploads the base image
        if 'inimage' not in request.files:
            flash('No file part')
            scratch = True
            # return redirect(request.url)
        user_image = request.files['inimage']
        base_image = user_image.filename
        print(base_image)
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if base_image == '':
            flash('No selected file')
            scratch = True
            # return redirect(request.url)
        if user_image and allowed_file(user_image.filename):
            filename = secure_filename(user_image.filename)
            user_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Resizing the image if necessary
        if user_image:
            image_to_resize = Image.open(f"apps/static/assets/img/bases/{base_image}")
            print(image_to_resize.size[0])
            horizontal = False
            proportion = 0
            if image_to_resize.size[0] >= image_to_resize.size[1]:
                image_ratio = image_to_resize.size[0] / image_to_resize.size[1]
                horizontal = True
                for n in reversed(range(1, 9)):
                    if image_to_resize.size[0] < 512:
                        new_image = image_to_resize.resize(512, 512/image_ratio)
                        proportion = 1
                        new_image.save(f"apps/static/assets/img/bases/{base_image}")
                    elif image_to_resize.size[0] > 1024:
                        new_image = image_to_resize.resize(1024, 1024/image_ratio)
                        proportion = 8
                        new_image.save(f"apps/static/assets/img/bases/{base_image}")
                    elif (512 + (n-1) * 64) < image_to_resize.size[0] <= (512 + n * 64):
                        new_width = 512 + n * 64
                        new_height = int(new_width / image_ratio)
                        new_image = image_to_resize.resize((new_width, new_height))
                        proportion = n
                        new_image.save(f"apps/static/assets/img/bases/{base_image}")
            else:
                image_ratio = image_to_resize.size[1] / image_to_resize.size[0]
                for n in reversed(range(1, 9)):
                    if image_to_resize.size[1] < 512:
                        new_image = image_to_resize.resize(512/image_ratio, 512)
                        proportion = 1
                        new_image.save(f"apps/static/assets/img/bases/{base_image}")
                    elif image_to_resize.size[1] > 1024:
                        new_image = image_to_resize.resize(1024/image_ratio, 1024)
                        proportion = 8
                        new_image.save(f"apps/static/assets/img/bases/{base_image}")
                    elif (512 + (n-1) * 64) < image_to_resize.size[0] <= (512 + n * 64):
                        new_height = 512 + n * 64
                        new_width = new_height / image_ratio
                        new_image = image_to_resize.resize((new_width, new_height))
                        proportion = n
                        new_image.save(f"apps/static/assets/img/bases/{base_image}")

            # Cropping the image if necessary
            image_to_crop = Image.open(f"apps/static/assets/img/bases/{base_image}")
            print(image_to_crop.size)
            if horizontal and image_to_crop.size[1] % 64 > 0:
                left = 0
                right = 512 + proportion * 64
                top = image_to_crop.size[1] % 64 / 2
                bottom = image_to_crop.size[1] - image_to_crop.size[1] % 64 / 2
                box = (left, top, right, bottom)
                cropped_image = image_to_crop.crop(box)
                cropped_image.save(f"apps/static/assets/img/bases/{base_image}")
            elif not horizontal and image_to_crop.size[0] % 64 > 0:
                left = image_to_crop.size[0] % 64 / 2
                right = image_to_crop.size[0] - image_to_crop.size[0] % 64 / 2
                top = 0
                bottom = 512 + proportion * 64
                box = (left, top, right, bottom)
                cropped_image = image_to_crop.crop(box)
                cropped_image.save(f"apps/static/assets/img/bases/{base_image}")

        if request.form.get("scratch"):
            scratch = True

        # Generates the new image
        stability_generation(my_prompt, base_image, wanted_samples, image_name, height, width, var=False, scratch=scratch)
        session_id_list = [d[0] for d in db.session.query(AImages.session_id).filter_by(username=username).all()]
        session_id = max(session_id_list)
        variation_params["prompt"] = my_prompt
        # return redirect(url_for('result', session_id=session_id))
    all_images = db.session.query(AImages).filter_by(session_id=session_id).filter_by(username=username).all()
    return render_template('home/studio.html', images=all_images, session_id=session_id, styles=styles,
                           moods=color_moods, rooms=room_types, samples=wanted_samples,)
