
from apps import db


class AImages(db.Model):

    __tablename__ = "user_images"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(250), nullable=False)
    prompt = db.Column(db.String(1000), nullable=False)
    image_name = db.Column(db.String(250), nullable=False)
    gen_image = db.Column(db.String(250), unique=True, nullable=False)
    base_image = db.Column(db.String(250), nullable=True)
    style = db.Column(db.String(250), nullable=True)
    room_type = db.Column(db.String(250), nullable=True)
    color_mood = db.Column(db.String(250), nullable=True)
    light_mood = db.Column(db.String(250), nullable=True)
    materials = db.Column(db.String(250), nullable=True)
    variant = db.Column(db.Boolean, nullable=False)
    bookmark = db.Column(db.Boolean, default=False, nullable=False)
    collection = db.Column(db.String(250), nullable=True)
    ratio = db.Column(db.String(250), nullable=True)
    date_time = db.Column(db.DateTime, nullable=False)
    quality = db.Column(db.String(250), nullable=True)


class Collects(db.Model):

    __tablename__ = "collections"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), nullable=False)
    collection = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(1500), nullable=True)

