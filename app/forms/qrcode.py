from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length, URL, Optional, NumberRange

from app.utils.validators import validate_url as _validate_url
from app.forms import CommaSeparatedMultipleField


class QRForm(FlaskForm):
    name = StringField('QR Name', validators=[DataRequired(), Length(min=2, max=100)])
    link = StringField('Link', validators=[DataRequired(), URL(message='Please enter a valid URL.')])
    user_id = SelectField('User', validators=[DataRequired()], coerce=int)
    category_ids = CommaSeparatedMultipleField('Categories', coerce=int, validators=[Optional()])
    fill_color = StringField('Fill Color', default='#000000',
                             validators=[Length(7, 7)])
    back_color = StringField('Background Color', default='#FFFFFF',
                             validators=[Length(7, 7)])
    scale = SelectField('Size', coerce=int, default=10,
                        choices=[(5, 'Small'), (8, 'Medium'), (10, 'Large'), (15, 'XL'), (20, 'XXL')],
                        validators=[Optional()])
    logo_scale = SelectField('Logo Size', coerce=int, default=5,
                             choices=[(3, '33%'), (4, '25%'), (5, '20%'), (6, '16%')],
                             validators=[Optional()])

    def validate_link(self, field):
        if not _validate_url(field.data):
            from wtforms.validators import ValidationError
            raise ValidationError('Only HTTP/HTTPS URLs are allowed. Localhost URLs are blocked.')


class EditQRForm(FlaskForm):
    name = StringField('QR Name', validators=[DataRequired(), Length(min=2, max=100)])
    link = StringField('Link', validators=[DataRequired(), URL(message='Please enter a valid URL.')])
    user_id = SelectField('User', validators=[DataRequired()], coerce=int)
    category_ids = CommaSeparatedMultipleField('Categories', coerce=int, validators=[Optional()])
    fill_color = StringField('Fill Color', validators=[Length(7, 7)])
    back_color = StringField('Background Color', validators=[Length(7, 7)])
    scale = SelectField('Size', coerce=int,
                        choices=[(5, 'Small'), (8, 'Medium'), (10, 'Large'), (15, 'XL'), (20, 'XXL')],
                        validators=[Optional()])
    logo_scale = SelectField('Logo Size', coerce=int, default=5,
                             choices=[(3, '33%'), (4, '25%'), (5, '20%'), (6, '16%')],
                             validators=[Optional()])

    def validate_link(self, field):
        if not _validate_url(field.data):
            from wtforms.validators import ValidationError
            raise ValidationError('Only HTTP/HTTPS URLs are allowed. Localhost URLs are blocked.')
