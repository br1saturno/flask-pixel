import os
import io
import warnings
from apps import db
from apps.studio.models import AImages
from flask import request
from flask_login import login_required
from apps.authentication.models import Users
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
    "width": 512,
    "height": 512,
    "image_details": "",
    "originals": 1,
}


def stability_generation(my_prompt, base_image_url, wanted_samples, image_name, height, width, var: bool, scratch: bool):
    """ The var parameter is False for a new session and True for variations in the same session """
    username = None
    if current_user.is_authenticated:
        user_id = current_user.get_id()
        username = str(Users.query.filter_by(id=user_id).first())
    print(username)
    if scratch:
        base_image = None
        answers = stability_api.generate(
            prompt=my_prompt,
            init_image=base_image,
            start_schedule=0.6,
            # guidance_strength=0.25,
            # mask_image=base_image,
            samples=wanted_samples,
            height=height,
            width=width,
            # steps=100,
            # cfg_scale=7.0,
            # seed=2895508001,
            # guidance_prompt=my_prompt
        )
    elif not var:
        base_image = Image.open(f"apps/static/assets/img/bases/{base_image_url}")
        answers = stability_api.generate(
            prompt=my_prompt,
            init_image=base_image,
            start_schedule=0.6,
            # guidance_strength=0.25,
            # mask_image=base_image,
            samples=wanted_samples,
            # height=height,
            # width=width,
            # steps=50,
            # cfg_scale=7.0,
            # seed=2895508001,
            # guidance_prompt=my_prompt
        )
    else:
        base_image = Image.open(f"apps/static/assets/img/generated/{base_image_url}")
        answers = stability_api.generate(
            prompt=my_prompt,
            init_image=base_image,
            start_schedule=0.6,
            # guidance_strength=0.25,
            # mask_image=base_image,
            samples=wanted_samples,
            # height=height,
            # width=width,
            # steps=50,
            # cfg_scale=7.0,
            # seed=2895508001,
            # guidance_prompt=my_prompt
        )

    # Loads the session number so it knows which images to load
    session_id_list = [d[0] for d in db.session.query(AImages.session_id).filter_by(username=username).all()]
    if not var and len(session_id_list) > 0:
        session_id = max(session_id_list) + 1
    elif var and len(session_id_list) > 0:
        session_id = max(session_id_list)
    else:
        session_id = 1

    # Indicates the session in which the variations will be made
    variation_params["session"] = session_id

    n = 1  # Image counter for each sample

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
                # generated_images.append(f"{image_name}{n}.png")

                img.save(f"apps/static/{image_png}")
                # Saves the image to the database
                new_image = AImages(session_id=session_id, username=username, prompt=my_prompt, image_name=image_name,
                                    gen_image=image_png, base_image=base_image_url)
                db.session.add(new_image)
                db.session.commit()
                gen_list = [d[0] for d in db.session.query(AImages.gen_image).filter_by(username=username, session_id=session_id).all()]
                print(gen_list)
                n += 1
                if not var:
                    variation_params[f"{n}"] = []

    if not var:
        variation_params["originals"] = n


def resize_image(user_image, base_image):
    # Resizing the image if necessary
    resized_image = ""
    if user_image:
        image_to_resize = Image.open(f"apps/static/assets/img/bases/{base_image}")
        horizontal = False
        proportion = 0
        if image_to_resize.size[ 0 ] >= image_to_resize.size[ 1 ]:
            image_ratio = image_to_resize.size[ 0 ] / image_to_resize.size[ 1 ]
            horizontal = True
            for n in reversed(range(1, 9)):
                if image_to_resize.size[ 0 ] < 512:
                    new_image = image_to_resize.resize(512, 512 / image_ratio)
                    proportion = 1
                    new_image.save(f"apps/static/assets/img/bases/{base_image}")
                elif image_to_resize.size[ 0 ] > 1024:
                    new_image = image_to_resize.resize(1024, 1024 / image_ratio)
                    proportion = 8
                    new_image.save(f"apps/static/assets/img/bases/{base_image}")
                elif (512 + (n - 1) * 64) < image_to_resize.size[ 0 ] <= (512 + n * 64):
                    new_width = 512 + n * 64
                    new_height = int(new_width / image_ratio)
                    new_image = image_to_resize.resize((new_width, new_height))
                    proportion = n
                    new_image.save(f"apps/static/assets/img/bases/{base_image}")
        else:
            image_ratio = image_to_resize.size[ 1 ] / image_to_resize.size[ 0 ]
            for n in reversed(range(1, 9)):
                if image_to_resize.size[ 1 ] < 512:
                    new_image = image_to_resize.resize(512 / image_ratio, 512)
                    proportion = 1
                    new_image.save(f"apps/static/assets/img/bases/{base_image}")
                elif image_to_resize.size[ 1 ] > 1024:
                    new_image = image_to_resize.resize(1024 / image_ratio, 1024)
                    proportion = 8
                    new_image.save(f"apps/static/assets/img/bases/{base_image}")
                elif (512 + (n - 1) * 64) < image_to_resize.size[ 0 ] <= (512 + n * 64):
                    new_height = 512 + n * 64
                    new_width = new_height / image_ratio
                    new_image = image_to_resize.resize((new_width, new_height))
                    proportion = n
                    new_image.save(f"apps/static/assets/img/bases/{base_image}")

        # Cropping the image if necessary
        image_to_crop = Image.open(f"apps/static/assets/img/bases/{base_image}")
        if horizontal and image_to_crop.size[ 1 ] % 64 > 0:
            left = 0
            right = 512 + proportion * 64
            top = image_to_crop.size[ 1 ] % 64 / 2
            bottom = image_to_crop.size[ 1 ] - image_to_crop.size[ 1 ] % 64 / 2
            box = (left, top, right, bottom)
            cropped_image = image_to_crop.crop(box)
            cropped_image.save(f"apps/static/assets/img/bases/{base_image}")
        elif not horizontal and image_to_crop.size[ 0 ] % 64 > 0:
            left = image_to_crop.size[ 0 ] % 64 / 2
            right = image_to_crop.size[ 0 ] - image_to_crop.size[ 0 ] % 64 / 2
            top = 0
            bottom = 512 + proportion * 64
            box = (left, top, right, bottom)
            cropped_image = image_to_crop.crop(box)
            cropped_image.save(f"apps/static/assets/img/bases/{base_image}")


def variation(variation_image, username, session_id):
    print(username, session_id)
    base_image = variation_image.split('/')[3]
    generated_images = [d[0] for d in db.session.query(AImages.gen_image).filter_by(username=username, session_id=session_id).all()]
    print(generated_images)
    img_index = generated_images.index(variation_image)
    if f"{img_index + 1}" in variation_params:
        if len(variation_params[f"{img_index + 1}"]) == 0:
            variation_number = 1
            variation_params[f"{img_index + 1}"].append(variation_number)
        else:
            variation_number = len(variation_params[f"{img_index + 1}"]) + 1
            variation_params[f"{img_index + 1}"].append(variation_number)
    else:
        variation_params[f"{img_index + 1}"] = []
        variation_number = 1
        variation_params[f"{img_index + 1}"].append(variation_number)
    new_name = f"{base_image.split('.')[ 0 ]}-{variation_number}"

    stability_generation(variation_params["prompt"], base_image, 1, new_name, variation_params["height"], variation_params["width"], True, False)

