import base64
import logging
from flask import flash

logger = logging.getLogger(__name__)


def flash_form_errors(form):
    """Flash all form validation errors with field names."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'Ошибка в поле {field}: {error}', 'danger')


def encode_image_base64(image_data: bytes) -> str | None:
    """Encode binary image data to base64 string."""
    if image_data:
        return base64.b64encode(image_data).decode('utf-8')
    return None
