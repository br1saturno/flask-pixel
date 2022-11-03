
from apps import db


class AImages(db.Model):

    __tablename__ = "user_images"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(250), nullable=False)
    prompt = db.Column(db.String(1000), nullable=False)
    image_name = db.Column(db.String(250), nullable=False)
    gen_image = db.Column(db.String(250), unique=True, nullable=False)
    base_image = db.Column(db.String(250), nullable=False)
