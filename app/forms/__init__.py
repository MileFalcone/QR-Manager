from wtforms import SelectMultipleField


class CommaSeparatedMultipleField(SelectMultipleField):
    """Handles comma-separated integer values from hidden input and/or checkboxes."""

    def process_formdata(self, valuelist):
        ids = []
        seen = set()
        for v in valuelist:
            if v:
                for part in v.split(','):
                    part = part.strip()
                    if part.isdigit() and part not in seen:
                        seen.add(part)
                        ids.append(int(part))
        self.data = ids

    def pre_validate(self, form):
        pass


from app.forms.auth import LoginForm
from app.forms.user import UserForm, EditUserForm
from app.forms.category import CategoryForm
from app.forms.qrcode import QRForm, EditQRForm

__all__ = ['LoginForm', 'UserForm', 'EditUserForm', 'CategoryForm', 'QRForm', 'EditQRForm',
           'CommaSeparatedMultipleField']
