from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import FileField


class UploadForm(FlaskForm):
    photo = FileField(validators=[FileRequired('no file!')])