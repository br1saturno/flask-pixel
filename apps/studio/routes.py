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
from apps.studio.util import variation_params
from apps.authentication.models import Users
from flask_login import login_required
from flask_login import (
    current_user
)
from jinja2 import TemplateNotFound

app = Flask(__name__)
app.register_blueprint(blueprint)

UPLOAD_FOLDER = '/static/assets/img/bases'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'sdlkfj$%^&fhgfghbdfg'
# sess = Session()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@blueprint.route('/studio', methods=['POST'])
@login_required
def generate_image():
    username = None
    if current_user.is_authenticated:
        username = current_user.get_id()
    session_id_list = [d[0] for d in db.session.query(AImages.session_id).filter_by(username=username).all()]
    session_id = max(session_id_list)

    # Loads the value for the stability ai function
    if request.method == "POST":
        my_prompt = f"A realistic photograph of a {request.form['room']}, {request.form['color_mood']} accent colors," \
                    f"{request.form['style']} furniture and accesories, 8k, unreal engine, highly detailed," \
                    f"octane render, sharp, ambient lighting"
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
    return render_template('studio.html', session_id=session_id)