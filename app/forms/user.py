from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, Optional

from app.models import User
from app.forms import CommaSeparatedMultipleField


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=128)])
    category_ids = CommaSeparatedMultipleField('Categories', coerce=int, validators=[Optional()])
    role = SelectField('Role', choices=[('user', 'User'), ('moderator', 'Moderator'), ('admin', 'Admin')], default='user')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            from wtforms.validators import ValidationError
            raise ValidationError('Username already exists.')


class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password (leave blank to keep current)',
                             validators=[Optional(), Length(min=4, max=128)])
    category_ids = CommaSeparatedMultipleField('Categories', coerce=int, validators=[Optional()])
    role = SelectField('Role', choices=[('user', 'User'), ('moderator', 'Moderator'), ('admin', 'Admin')], default='user')
