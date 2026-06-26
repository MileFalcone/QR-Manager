import io
import secrets
import logging

import segno
from PIL import Image, ImageDraw
from flask import url_for
from sqlalchemy.orm import joinedload, subqueryload

from app.extensions import db
from app.models import QRCode, Category

logger = logging.getLogger(__name__)


def _resolve_categories(category_ids) -> list[Category]:
    """Fetch Category objects from a list/str of IDs."""
    if not category_ids:
        return []
    if isinstance(category_ids, str):
        ids = [int(x.strip()) for x in category_ids.split(',') if x.strip().isdigit()]
    else:
        ids = category_ids
    return Category.query.filter(Category.id.in_(ids)).all()


def _hex_to_rgba(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip('#')
    return (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16), 255)


def _hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip('#')
    return (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))


def _render_qr_image(redirect_url: str, fill_color: str = '#000000',
                     back_color: str = '#FFFFFF', scale: int = 10,
                     logo_image: bytes | None = None,
                     logo_scale: int = 5) -> bytes:
    """Render a QR code PNG image with customization options.

    Supports fill/background color and embedded logo image.
    When a logo is embedded, error correction is raised to 'H' (30%)
    for reliable scanning.
    """
    if not logo_image:
        qr = segno.make_qr(redirect_url)
        buf = io.BytesIO()
        qr.save(buf, kind='png', scale=scale, dark=fill_color, light=back_color)
        return buf.getvalue()

    qr = segno.make_qr(redirect_url, error='h')
    matrix = qr.matrix
    modules = len(matrix)

    render_factor = 4
    ms = scale * render_factor
    size = modules * ms

    bg_rgba = _hex_to_rgba(back_color)
    fg_rgba = _hex_to_rgba(fill_color)

    img = Image.new('RGBA', (size, size), bg_rgba)
    draw = ImageDraw.Draw(img)

    for y in range(modules):
        for x in range(modules):
            if matrix[y][x]:
                x0, y0 = x * ms, y * ms
                x1, y1 = x0 + ms, y0 + ms
                draw.rectangle([x0, y0, x1, y1], fill=fg_rgba)

    try:
        logo = Image.open(io.BytesIO(logo_image)).convert('RGBA')
        logo_max = size // logo_scale
        logo.thumbnail((logo_max, logo_max), Image.LANCZOS)
        lx = (size - logo.width) // 2
        ly = (size - logo.height) // 2
        pad = ms * 2
        cx = lx + logo.width // 2
        cy = ly + logo.height // 2
        cr = max(logo.width, logo.height) // 2 + pad
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill='white')
        img.paste(logo, (lx, ly), logo)
    except Exception:
        logger.warning('Failed to embed logo image', exc_info=True)

    final_size = modules * scale
    img = img.resize((final_size, final_size), Image.LANCZOS)

    result = Image.new('RGB', (final_size, final_size), _hex_to_rgb(back_color))
    result.paste(img, mask=img.split()[3])

    buf = io.BytesIO()
    result.save(buf, 'PNG')
    return buf.getvalue()


def generate_qr_code(name: str, link: str, user_id: int,
                     category_ids=None, fill_color='#000000',
                     back_color='#FFFFFF', scale=10,
                     logo_image=None, logo_scale=5) -> QRCode:
    """Generate a new QR code with a redirect link."""
    qr_key = secrets.token_urlsafe(8)
    redirect_url = url_for('main.redirect_to_link', key=qr_key, _external=True)

    img_data = _render_qr_image(redirect_url, fill_color, back_color, scale,
                                logo_image, logo_scale)

    new_qr = QRCode(
        name=name,
        link=link,
        key=qr_key,
        image_data=img_data,
        fill_color=fill_color,
        back_color=back_color,
        scale=scale,
        logo_image=logo_image,
        logo_scale=logo_scale,
        user_id=user_id,
    )
    selected = _resolve_categories(category_ids)
    new_qr.categories.extend(selected)

    db.session.add(new_qr)
    db.session.commit()
    logger.info(f'QR code generated: {name}')
    return new_qr


def update_qr_code(qr_entry: QRCode, name: str, link: str, user_id: int,
                   category_ids=None, fill_color='#000000',
                   back_color='#FFFFFF', scale=10,
                   logo_image=None, logo_scale=5) -> QRCode:
    """Update an existing QR code record and regenerate its image."""
    qr_entry.name = name
    qr_entry.link = link
    qr_entry.user_id = user_id
    qr_entry.categories = _resolve_categories(category_ids)

    qr_entry.fill_color = fill_color
    qr_entry.back_color = back_color
    qr_entry.scale = scale
    qr_entry.logo_scale = logo_scale

    if logo_image is not None:
        qr_entry.logo_image = logo_image

    redirect_url = url_for('main.redirect_to_link', key=qr_entry.key, _external=True)
    qr_entry.image_data = _render_qr_image(
        redirect_url, fill_color, back_color, scale,
        qr_entry.logo_image, logo_scale
    )

    db.session.commit()
    logger.info(f'QR code updated: {qr_entry.name}')
    return qr_entry


def delete_qr_code(qr_entry: QRCode) -> None:
    """Delete a QR code record."""
    db.session.delete(qr_entry)
    db.session.commit()
    logger.info(f'QR code deleted: {qr_entry.id}')


def get_qr_code_with_relations(qr_id: int) -> QRCode | None:
    """Get a QR code with owner and categories eagerly loaded."""
    return QRCode.query.options(
        joinedload(QRCode.owner),
        subqueryload(QRCode.categories),
    ).get(qr_id)


def get_paginated_qrcodes(page: int = 1, per_page: int = 20):
    """Get paginated QR codes with eager-loaded relations."""
    return QRCode.query.options(
        joinedload(QRCode.owner),
        subqueryload(QRCode.categories),
    ).order_by(QRCode.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
