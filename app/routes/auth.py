import io
import base64
import logging
import random

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from PIL import Image, ImageDraw

from app.extensions import db
from app.models import User
from app.forms import LoginForm
from app.utils.helpers import flash_form_errors

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

_COLORS = [
    ('red', (220, 50, 50), 'красных'),
    ('blue', (50, 80, 220), 'синих'),
    ('green', (50, 180, 70), 'зелёных'),
    ('yellow', (230, 190, 30), 'жёлтых'),
    ('purple', (160, 50, 200), 'фиолетовых'),
    ('orange', (220, 130, 30), 'оранжевых'),
]
_SHAPES = [('circle', 'кругов'), ('square', 'квадратов'), ('triangle', 'треугольников')]


def _draw_shape(draw, shape, x, y, size, color):
    if shape == 'circle':
        draw.ellipse([x, y, x + size, y + size], fill=color, outline=(60, 60, 60))
    elif shape == 'square':
        draw.rectangle([x, y, x + size, y + size], fill=color, outline=(60, 60, 60))
    elif shape == 'triangle':
        draw.polygon([(x + size // 2, y), (x, y + size), (x + size, y + size)], fill=color, outline=(60, 60, 60))


def generate_captcha():
    width, height = 260, 130
    img = Image.new('RGB', (width, height), (250, 250, 250))
    draw = ImageDraw.Draw(img)

    drawn = []
    for _ in range(random.randint(4, 7)):
        color_name, color_rgb, _ = random.choice(_COLORS)
        shape_name, _ = random.choice(_SHAPES)
        x = random.randint(10, width - 40)
        y = random.randint(10, height - 40)
        s = random.randint(20, 38)
        _draw_shape(draw, shape_name, x, y, s, color_rgb)
        drawn.append({'type': shape_name, 'color': color_name})

    for _ in range(random.randint(3, 5)):
        draw.line([(random.randint(0, width), random.randint(0, height)),
                   (random.randint(0, width), random.randint(0, height))],
                  fill=random.randint(180, 210), width=1)

    if random.choice([True, False]):
        valid = [(c, n) for c, _, n in _COLORS if sum(1 for d in drawn if d['color'] == c) >= 1]
        target, ru = random.choice(valid)
        answer = sum(1 for d in drawn if d['color'] == target)
        question = f'Сколько {ru} фигур?'
    else:
        valid = [(s, n) for s, n in _SHAPES if sum(1 for d in drawn if d['type'] == s) >= 1]
        target, ru = random.choice(valid)
        answer = sum(1 for d in drawn if d['type'] == target)
        question = f'Сколько {ru}?'

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    session['captcha_answer'] = answer
    return {
        'image': f'data:image/png;base64,{img_b64}',
        'question': question,
    }


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        if form.captcha.data != session.pop('captcha_answer', None):
            flash('Неверный ответ капчи!', 'danger')
            return render_template('auth/login.html', form=form, captcha_image=generate_captcha())

        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            logger.info(f'User {user.username} logged in')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Неверное имя пользователя или пароль!', 'danger')
    else:
        flash_form_errors(form)

    return render_template('auth/login.html', form=form, captcha_image=generate_captcha())


@auth_bp.route('/logout')
@login_required
def logout():
    logger.info(f'User {current_user.username} logged out')
    logout_user()
    flash('Вы успешно вышли из системы!', 'info')
    return redirect(url_for('main.index'))
