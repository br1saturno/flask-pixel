import os
import io
import warnings
from apps.studio import blueprint
from flask import Flask, flash, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
from apps.studio.util import stability_generation
from apps import db
from apps.studio.models import AImages
from apps.studio.forms import StudioForm, styles, color_moods, room_types, color_moods_dict
from apps.studio.util import variation_params
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
        my_prompt = f"A realistic photograph of a {request.form['room']}, {colors}," \
                    f"{request.form['style']} furniture and {request.form['style']} accesories, 8k, unreal engine, " \
                    f"highly detailed, octane render, sharp, ambient lighting"
        print(my_prompt)
        print(color_moods_dict)
        image_name = request.form["iname"]
        wanted_samples = int(request.form["amountInput"])

        # Uploads the base image
        if 'inimage' not in request.files:
            flash('No file part')
            return redirect(request.url)
        user_image = request.files['inimage']
        base_image = user_image.filename

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if base_image == '':
            flash('No selected file')
            return redirect(request.url)
        if user_image and allowed_file(user_image.filename):
            filename = secure_filename(user_image.filename)
            user_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Generates the new image
        stability_generation(my_prompt, base_image, wanted_samples, image_name, False)
        session_id_list = [d[0] for d in db.session.query(AImages.session_id).filter_by(username=username).all()]
        session_id = max(session_id_list)
        variation_params["prompt"] = my_prompt
        # return redirect(url_for('result', session_id=session_id))
    all_images = db.session.query(AImages).filter_by(session_id=session_id).filter_by(username=username).all()
    return render_template('home/studio.html', images=all_images, session_id=session_id, styles=styles,
                           moods=color_moods, rooms=room_types)
