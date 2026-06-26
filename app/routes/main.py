import logging

from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models import QRCode
from app.utils.validators import validate_url
from app.utils.helpers import encode_image_base64

logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_qrcodes = current_user.get_shared_qrcodes().all()

    processed_qrcodes = [
        {
            'id': qr.id,
            'name': qr.name,
            'link': qr.link,
            'image_b64': encode_image_base64(qr.image_data),
            'categories': [cat.name for cat in qr.categories],
        }
        for qr in user_qrcodes
    ]

    return render_template(
        'main/dashboard.html',
        name=current_user.username,
        qrcodes=processed_qrcodes,
    )


@main_bp.route('/api')
def api_docs():
    return render_template('main/api.html')


@main_bp.route('/r/<string:key>')
def redirect_to_link(key):
    qr_entry = QRCode.query.filter_by(key=key).first_or_404()

    if not validate_url(qr_entry.link):
        logger.warning(f'Invalid URL in QR code {qr_entry.id}: {qr_entry.link}')
        abort(400, 'Invalid URL')

    logger.info(f'Redirect via QR code: {qr_entry.name} -> {qr_entry.link}')
    return redirect(qr_entry.link)
