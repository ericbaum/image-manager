from datetime import datetime
import re
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from .app import app
from .utils import HTTPRequestError
from .conf import CONFIG
from sqlalchemy.exc import IntegrityError
from minio import Minio

app.config['SQLALCHEMY_DATABASE_URI'] = CONFIG.get_db_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


minioClient = Minio(CONFIG.s3url, CONFIG.s3user, CONFIG.s3pass, secure=False)


class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.String(36), unique=True, nullable=False, primary_key=True)
    label = db.Column(db.String(128), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.now)

    fw_version = db.Column(db.String(128), nullable=False)
    sha1 = db.Column(db.String(40), nullable=False)
    confirmed = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return "<Image(label={}, fw_version={})>".format(self.label, self.fw_version)


def assert_image_exists(image_id):
    try:
        return Image.query.filter_by(id=image_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        raise HTTPRequestError(404, "No such image: %s" % image_id)


def get_all_images():
    return Image.query.all()


def handle_consistency_exception(error):
    # message = error.message.replace('\n','')
    message = re.sub(r"(^\(.*?\))|\n", "", error.message)
    raise HTTPRequestError(400, message)
