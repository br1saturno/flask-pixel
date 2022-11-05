import os
import io
import warnings

from apps import db
from apps.studio.models import AImages
from flask_login import login_required
from flask_login import (
    current_user
)

from PIL import Image # image processing

from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation


stability_api = client.StabilityInference(key=os.environ['STABILITY_KEY'], verbose=True, )

variation_params = {
    "prompt": "",
    "session": 0,
}


def stability_generation(my_prompt, base_image_url, wanted_samples, image_name, var: bool):
    """ The var parameter is False for a new session and True for variations in the same session """
    username = None
    if current_user.is_authenticated:
        username = current_user.get_id()
    base_image = Image.open(f"static/assets/img/bases/{base_image_url}")
    answers = stability_api.generate(
        prompt=my_prompt,
        init_image=base_image,
        start_schedule=0.6,
        # guidance_strength=0.25,
        # mask_image=base_image,
        samples=wanted_samples,
        # height=512,
        # width=512,
        # steps=50,
        # cfg_scale=7.0,
        # seed=2895508001,
        # guidance_prompt=my_prompt
    )

    n = 1 # Image counter for each session

    # Loads the session number so it knows which images to load
    session_id_list = [d[0] for d in db.session.query(AImages.session_id).filter_by(username=username).all()]
    if not var and len(session_id_list) > 0:
        session_id = max(session_id_list) + 1
    elif var and len(session_id_list) > 0:
        session_id = max(session_id_list)
    else:
        session_id = 1

    # Indicates the session in which the variations are being made
    variation_params["session"] = session_id

    # Generates the image/s
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn("Your request activated the API's safety filters and could not be processed."
                              "Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                if img.mode in ('P', '1'):
                    img = img.convert("RGB")
                # new_base = Base(username="bruno", session_id=session_id, base_image=base_image_url)
                # db.session.add(new_base)
                # db.session.commit()
                image_png = f"assets/img/generated/{image_name}{n}.png"
                img.save(f"static/{image_png}")
                # Saves the image to the database
                new_image = AImages(session_id=session_id, username=USERNAME, prompt=my_prompt, image_name=image_name,
                                    gen_image=image_png, base_image=base_image_url)
                db.session.add(new_image)
                db.session.commit()
                n += 1
