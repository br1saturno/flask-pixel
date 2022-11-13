import os
import io
import warnings

import apps.studio.util
from apps.studio import blueprint
from flask import Flask, flash, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
from apps import db
from PIL import Image

from apps.studio.models import AImages
from apps.studio.forms import StudioForm, styles, color_moods, room_types, color_moods_dict, aspect_ratio, aspect_ratio_low
from apps.studio.util import stability_generation, variation_params, resize_image, variation
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
@blueprint.route('/studio/<int:var>/<variation_image>', methods=['GET', 'POST'])
@login_required
def generate_image(var=0, variation_image='none'):
    username = None

    if current_user.is_authenticated:
        user_id = current_user.get_id()
        username = str(Users.query.filter_by(id=user_id).first())

    scratch = False
    wanted_samples = 1
    room_input = ""
    style_input = ""
    color_input = ""
    ratio_input = ""
    images_details = ""
    width = 512
    height = 512
    image_name = ''
    user_image = ''
    base_image = ''
    my_prompt = ''
    session_id = 0

    # Loads the values for the stability ai function
    if request.method == "POST":
        if var == 0:
            session_id_list = [d[0] for d in db.session.query(AImages.session_id).filter_by(username=username).all()]
            if len(session_id_list) > 0:
                session_id = max(session_id_list) + 1
            else:
                session_id = 1
            # Values for the prompt
            colors = f""
            for color in color_moods_dict[request.form['color_mood']]:
                if color is color_moods_dict[request.form['color_mood']][0]:
                    colors = f"{color} accents"
                else:
                    colors += f", {color} accents"
            for pair in room_types:
                if request.form['room'] == pair[0]:
                    room_input = pair[1].split("-")[1]
            for pair in styles:
                if request.form['style'] == pair[0]:
                    style_input = pair[1]
            for pair in color_moods:
                if request.form['color_mood'] == pair[0]:
                    color_input = pair[1]

            my_prompt = f"A realistic photograph of a{room_input}, {colors}, " \
                        f"{style_input} furniture and {style_input} accesories, 8k, unreal engine, " \
                        f"highly detailed, octane render, sharp, ambient lighting"
            print(my_prompt)

            image_name = f"{username}-{session_id}-{request.form['room']}"
            print(image_name)

            wanted_samples = int(request.form["amountRange"])

            # Uploads the base image
            if 'inimage' not in request.files:
                flash('No file part')
                scratch = True
                # return redirect(request.url)

            if not scratch:
                user_image = request.files['inimage']
                base_image = user_image.filename
            else:
                for pair in aspect_ratio:
                    if request.form['ratio'] == pair[0]:
                        ratio_input = pair[1]
                width = aspect_ratio_low[request.form["ratio"]][0]
                height = aspect_ratio_low[request.form["ratio"]][1]

            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            # if base_image == '':
            #     flash('No selected file')
            #     scratch = True
                # return redirect(request.url)

            if user_image and allowed_file(user_image.filename):
                filename = secure_filename(user_image.filename)
                user_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            resize_image(user_image, base_image)

            # This string goes in the info popover of the results section
            images_details = f"{room_input}, {style_input} style, {color_input} color accents. Aspect ratio {ratio_input}. - Click again to dismiss -"
            variation_params["image_details"] = images_details
            variation_params["prompt"] = my_prompt

            if request.form.get("scratch"):
                scratch = True
                variation_params["width"] = aspect_ratio_low[request.form["ratio"]][0]
                variation_params["height"] = aspect_ratio_low[request.form["ratio"]][1]
            else:
                resized_image = Image.open(f"apps/static/assets/img/bases/{base_image}")
                variation_params["width"] = resized_image.size[0]
                variation_params["height"] = resized_image.size[1]

            # Generates the new image
            stability_generation(my_prompt, base_image, wanted_samples, image_name, height, width, var=False,
                                 scratch=scratch)
        else:
            session_id_list = [d[0] for d in db.session.query(AImages.session_id).filter_by(username=username).all()]
            session_id = max(session_id_list)
            print(username, session_id)
            generated_images = [d[0] for d in db.session.query(AImages.gen_image).filter_by(username=username, session_id=session_id).all()]
            print(generated_images)
            image_to_variate = generated_images[int(variation_image) - 1]
            print(image_to_variate)
            variation(image_to_variate, username, session_id)
            images_details = variation_params["image_details"]

        session_id_list = [d[0] for d in db.session.query(AImages.session_id).filter_by(username=username).all()]
        session_id = max(session_id_list)
        print(session_id)
    all_images = db.session.query(AImages).filter_by(session_id=session_id).filter_by(username=username).all()
    return render_template('home/studio.html', images=all_images, session_id=session_id, styles=styles,
                           moods=color_moods, rooms=room_types, samples=wanted_samples, details=images_details)



