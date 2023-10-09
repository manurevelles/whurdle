from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import InputRequired, NumberRange

class NumberForm(FlaskForm):
    number = IntegerField("Guess a number:", validators=[InputRequired(), NumberRange(1, 100)])
    submit = SubmitField("Submit")

class HurdleForm(FlaskForm):
    guess = StringField("Guess a word:", validators=[InputRequired()])
    submit = SubmitField("Submit")

class WhurdleForm(FlaskForm):
    guess = StringField("Guess a word:", validators=[InputRequired()])
    submit = SubmitField("Submit")
