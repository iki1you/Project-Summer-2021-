from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class FriendAddForm(FlaskForm):
    username = StringField('Никнэйм', validators=[DataRequired()])
    submit = SubmitField('Добавить')