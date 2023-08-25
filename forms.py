from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, SelectField
from wtforms.validators import DataRequired, URL, Email, Length, EqualTo
from flask_ckeditor import CKEditorField

##WTForm
class AddCourseForm(FlaskForm):
    course_units = IntegerField("Course Units")
    course_grade = SelectField("Course Grade", choices=['A','B','C','D','E','F'], validators=[DataRequired()])
    submit = SubmitField("Submit to Calculate GPA")
    next = SubmitField("Add another Course")

class RegisterForm(FlaskForm):
    name=StringField(label='Name', validators=[DataRequired()])
    email = StringField(label='Email', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(label="Join Us")

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label="Log in")

class SemesterForm(FlaskForm):
    semester_name = StringField(label='Semester Title', validators=[DataRequired()])
    submit = SubmitField("Add Result to Your Page")