from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=(DataRequired(), Email()))
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Confirm Password", validators=(DataRequired(), EqualTo("password"))
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Username already exists")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Email already exists.")


class QuestionForm(FlaskForm):
    options = RadioField("Options: ", validators=[DataRequired()], default=1)
    submit = SubmitField("Next")


# class QuestionForm(FlaskForm):
#     options = RadioField("Options")  # 생성자 호출 없이 필드를 선언합니다.

#     def __init__(self, choices=None, *args, **kwargs):
#         super(QuestionForm, self).__init__(*args, **kwargs)
#         self.options.choices = choices if choices else []  # 동적으로 선택지 설정

#     submit = SubmitField("Next")
