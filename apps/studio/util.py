import getpass, os
import io
import warnings
from datetime import datetime
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

os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'

stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'],
    verbose=True,
    engine="stable-diffusion-768-v2-0",
)

image_params = {
    "prompt": "",
    "session": 0,
    "style": "",
    "room": "",
    "colors": "",
    "light": "",
    "material": "",
    "ratio": "",
    "gen_time": [],
    "quality": "",
    "width": 512,
    "height": 512,
    "image_details": "",
    "originals": 1,
}


def stability_generation(session_id, my_prompt, base_image_url, wanted_samples, image_name, height, width, var: bool, scratch: bool):
    """ The var parameter is False for a new session and True for variations in the same session """
    image_params["datetime"] = datetime.now()
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
            guidance_strength=0.25,
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
            guidance_strength=0.25,
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
            guidance_strength=0.25,
            # steps=50,
            # cfg_scale=7.0,
            # seed=2895508001,
            # guidance_prompt=my_prompt
        )

    # Loads the session number so it knows which images to load
    # session_id_list = [d[0] for d in db.session.query(AImages.session_id).filter_by(username=username).all()]
    # if not var and len(session_id_list) > 0:
    #     session_id = max(session_id_list) + 1
    # elif var and len(session_id_list) > 0:
    #     session_id = max(session_id_list)
    # else:
    #     session_id = 1

    # Indicates the session in which the variations will be made
    image_params["session"] = session_id

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
                style = image_params["style"]
                room_type = image_params[ "room" ]
                color_mood = image_params[ "colors" ]
                light_mood = image_params[ "light" ]
                materials = image_params[ "material" ]
                ratio = image_params[ "ratio" ]
                gen_time = image_params[ "datetime" ]
                quality = image_params[ "quality" ]
                new_image = AImages(session_id=session_id, username=username, prompt=my_prompt, image_name=image_name,
                                    gen_image=image_png, base_image=base_image_url, style=style, room_type=room_type,
                                    color_mood=color_mood, light_mood=light_mood, materials=materials, variant=var,
                                    bookmark=False, collection="", ratio=ratio, date_time=gen_time, quality=quality)
                db.session.add(new_image)
                db.session.commit()
                gen_list = [d[0] for d in db.session.query(AImages.gen_image).filter_by(username=username, session_id=session_id).all()]
                print(gen_list)
                n += 1
    #             if not var:
    #                 image_params[ f"{n}" ] = []
    #
    # if not var:
    #     image_params[ "originals" ] = n


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
                    new_image = image_to_resize.resize((512, int(512 / image_ratio)))
                    proportion = 1
                    new_image.save(f"apps/static/assets/img/bases/{base_image}")
                elif image_to_resize.size[ 0 ] > 1024:
                    new_image = image_to_resize.resize((1024, int(1024 / image_ratio)))
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
                    new_image = image_to_resize.resize((int(512 / image_ratio), 512))
                    proportion = 1
                    new_image.save(f"apps/static/assets/img/bases/{base_image}")
                elif image_to_resize.size[ 1 ] > 1024:
                    new_image = image_to_resize.resize(int((1024 / image_ratio), 1024))
                    proportion = 8
                    new_image.save(f"apps/static/assets/img/bases/{base_image}")
                elif (512 + (n - 1) * 64) < image_to_resize.size[ 0 ] <= (512 + n * 64):
                    new_height = 512 + n * 64
                    new_width = int(new_height / image_ratio)
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


def variation(variation_image_id, username):
    image_to_variate = db.session.query(AImages.gen_image).filter_by(id=variation_image_id).all()[0][0]
    all_session_ids = db.session.query(AImages.session_id).filter_by(username=username).all()
    session_id = max([d[0] for d in all_session_ids]) + 1
    base_image = image_to_variate.split('/')[3]
    print(f"ID: {variation_image_id} | Correspond to: {base_image}")
    image_size = Image.open(f"apps/static/{image_to_variate}").size
    generated_images = [d[0] for d in db.session.query(AImages.gen_image).filter_by(username=username, session_id=session_id).all()]
    n = 1
    new_name = f"{base_image.split('.')[0]}-v{session_id}{n}.png"
    while new_name in generated_images:
        n += 1
        new_name = f"{base_image.split('.')[0]}-v{session_id}{n}.png"
    new_name = new_name.split(".")[0]
    print(f"Variation name: {new_name}")
    variation_prompt = db.session.query(AImages.prompt).filter_by(id=variation_image_id).all()[0][0]
    variation_height = image_size[1]
    variation_width = image_size[0]
    image_params[ "prompt" ] = db.session.query(AImages.prompt).filter_by(id=variation_image_id).all()[ 0 ][ 0 ]
    image_params[ "style" ] = db.session.query(AImages.style).filter_by(id=variation_image_id).all()[ 0 ][ 0 ]
    image_params[ "room" ] = db.session.query(AImages.room_type).filter_by(id=variation_image_id).all()[ 0 ][ 0 ]
    image_params[ "colors" ] = db.session.query(AImages.color_mood).filter_by(id=variation_image_id).all()[ 0 ][ 0 ]
    image_params[ "light" ] = db.session.query(AImages.light_mood).filter_by(id=variation_image_id).all()[ 0 ][ 0 ]
    image_params[ "material" ] = db.session.query(AImages.materials).filter_by(id=variation_image_id).all()[ 0 ][ 0 ]
    image_params[ "quality" ] = db.session.query(AImages.quality).filter_by(id=variation_image_id).all()[ 0 ][ 0 ]
    image_params[ "ratio" ] = db.session.query(AImages.ratio).filter_by(id=variation_image_id).all()[ 0 ][ 0 ]

    stability_generation(session_id, variation_prompt, base_image, 1, new_name, variation_height, variation_width, True, False)


def content_loader(number_of_sessions, username, page):
    """ The page parameter is 1 for the Studio and 2 for the Gallery """
    showed_images_dict = {}
    details_dict = {}
    session_id_list = [d[0] for d in db.session.query(AImages.session_id).filter_by(username=username).all()]
    session_id = max(session_id_list)

    sessions_to_load = number_of_sessions
    all_sessions = db.session.query(AImages.session_id.distinct()).filter_by(username=username).all()
    all_sessions_list = [d[0] for d in all_sessions]
    if len(all_sessions_list) > sessions_to_load:
        for s in range(session_id - (sessions_to_load - 1), session_id + 1):
            showed_images = db.session.query(AImages.id, AImages.gen_image, AImages.bookmark).filter_by(session_id=s).filter_by(
                username=username).all()
            if page == 1:
                all_info = db.session.query(AImages).filter_by(session_id=s).filter_by(
                    username=username).all()
                details_dict[s] = f"A sample {all_info[0].prompt.split('.')[1].lower()}."
            showed_images_dict[s] = [d for d in showed_images]
            showed_sessions = all_sessions_list[-sessions_to_load:]
    else:
        for s in range(1, session_id + 1):
            showed_images = db.session.query(AImages.id, AImages.gen_image, AImages.bookmark).filter_by(session_id=s).filter_by(
                username=username).all()
            if page == 1:
                all_info = db.session.query(AImages).filter_by(session_id=s).filter_by(username=username).all()
                details_dict[s] = f"A sample {all_info[0].prompt.split('.')[1].lower()}. Aspect ratio: {all_info[0].ratio}."
            showed_images_dict[s] = [d for d in showed_images]
            showed_sessions = all_sessions_list
    return [showed_images_dict, details_dict]


def bookmark(image_id):
    image_to_bookmark = db.session.query(AImages).get(image_id)
    if not image_to_bookmark.bookmark:
        image_to_bookmark.bookmark = True
        db.session.commit()
    else:
        image_to_bookmark.bookmark = False
        db.session.commit()

