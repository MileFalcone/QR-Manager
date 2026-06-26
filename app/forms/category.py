from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length

from app.models import Category


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=50)])

    def validate_name(self, field):
        q = Category.query.filter_by(name=field.data)
        if hasattr(self, '_obj') and self._obj:
            q = q.filter(Category.id != self._obj.id)
        if q.first():
            from wtforms.validators import ValidationError
            raise ValidationError('Category already exists.')
