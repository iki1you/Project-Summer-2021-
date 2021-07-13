from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class MessageForm(FlaskForm):
    message = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField('Отправить')