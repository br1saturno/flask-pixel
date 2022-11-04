import os
import io
import warnings
from apps.studio import blueprint
from flask import Flask, flash, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
from apps.studio.util import stability_generation
from apps import db
from apps.studio.models import AImages
from apps.studio.forms import StudioForm
from apps.authentication.models import Users
from flask_login import login_required
from flask_login import (
    current_user
)
from jinja2 import TemplateNotFound

UPLOAD_FOLDER = './static/images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# blueprint.config['SESSION_TYPE'] = 'memcached'
# blueprint.config['SECRET_KEY'] = 'sdlkfj$%^&fhgfghbdfg'
# # sess = Session()
# blueprint.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@blueprint.route('/studio', methods=['POST'])
@login_required
def generate_image():
    username = None
    if current_user.is_authenticated:
        username = current_user.get_id()
    gen_form = StudioForm()
    # Loads the value for the stability ai function
    if request.method == "POST":
        my_prompt = request.form["prompt"]
        image_name = request.form["iname"]
        wanted_samples = int(request.form["samples"])

        # Uploads the base image
        if 'inimage' not in request.files:
            flash('No file part')
            return redirect(request.url)
        base_image = request.files['inimage']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if base_image.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if base_image and allowed_file(base_image.filename):
            filename = secure_filename(base_image.filename)
            base_image.save(os.path.join(blueprint.config['UPLOAD_FOLDER'], filename))

        # Generates the new image
        stability_generation(my_prompt, base_image.filename, wanted_samples, image_name, False)
        session_id_list = [d[0] for d in db.session.query(AImages.session_id).filter_by(username=username).all()]
        session_id = max(session_id_list)
        variation_params["prompt"] = my_prompt
        return redirect(url_for('result', session_id=session_id))
    return render_template('home/studio.html', form=gen_form)