import io
import logging

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, send_file
from flask_login import login_required, current_user

from app.extensions import db
from app.models import User, QRCode, Category, Setting
from app.forms import UserForm, EditUserForm, CategoryForm, QRForm, EditQRForm
from app.utils.helpers import flash_form_errors, encode_image_base64
from app.utils.validators import validate_url
from app.services import qr_service, user_service, category_service

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _require_admin():
    if current_user.role not in ('admin', 'moderator'):
        abort(403)


def _require_superadmin():
    if current_user.role != 'admin':
        abort(403)


# ─── Dashboard ───────────────────────────────────────────────────

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    _require_admin()

    per_page = 20
    users_page = request.args.get('users_page', 1, type=int)
    qrcodes_page = request.args.get('qrcodes_page', 1, type=int)

    users_pagination = user_service.get_paginated_users(page=users_page, per_page=per_page)
    qrcodes_pagination = qr_service.get_paginated_qrcodes(page=qrcodes_page, per_page=per_page)
    categories = Category.query.all()

    qrcodes_data = [
        {
            'id': qr.id,
            'name': qr.name,
            'link': qr.link,
            'user_id': qr.user_id,
            'owner': qr.owner.username if qr.owner else 'Unknown',
            'categories': [cat.name for cat in qr.categories],
            'created_at': qr.created_at,
        }
        for qr in qrcodes_pagination.items
    ]

    return render_template(
        'admin/dashboard.html',
        name=current_user.username,
        users=users_pagination.items,
        qrcodes=qrcodes_data,
        categories=categories,
        users_pagination=users_pagination,
        qrcodes_pagination=qrcodes_pagination,
    )


# ─── Site Settings ───────────────────────────────────────────────

@admin_bp.route('/site_settings', methods=['GET', 'POST'])
@login_required
def site_settings():
    _require_superadmin()

    if request.method == 'POST':
        sitename = request.form.get('sitename', '').strip()
        version = request.form.get('version', '').strip()
        if sitename:
            Setting.set('sitename', sitename)
        if version:
            Setting.set('version', version)
        flash('Настройки сайта успешно сохранены!', 'success')
        return redirect(url_for('admin.dashboard'))

    from flask import session
    from flask_wtf.csrf import generate_csrf
    csrf_token = generate_csrf()
    return render_template('admin/partials/settings_form.html',
                           sitename=Setting.get('sitename', 'QR Manager'),
                           version=Setting.get('version', 'v2.0'),
                           csrf_token=csrf_token)


# ─── Users CRUD ──────────────────────────────────────────────────

@admin_bp.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    _require_admin()

    form = UserForm()
    categories = Category.query.all()
    form.category_ids.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        try:
            user_service.create_user(
                username=form.username.data,
                password=form.password.data,
                role=form.role.data,
                category_ids=form.category_ids.data,
            )
            logger.info(f'Admin {current_user.username} created user: {form.username.data}')
            flash(f'Пользователь {form.username.data} успешно создан!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error creating user: {e}')
            flash(f'Ошибка при создании пользователя: {e}', 'danger')
    else:
        flash_form_errors(form)

    return render_template('admin/partials/create_user_form.html', form=form, categories=categories)


@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    _require_admin()

    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)

    categories = Category.query.all()
    form.category_ids.choices = [(c.id, c.name) for c in categories]

    if request.method == 'GET':
        form.category_ids.data = [c.id for c in user.categories]
        return render_template('admin/partials/edit_user_form.html', user=user, form=form, categories=categories)

    if form.validate_on_submit():
        try:
            if form.username.data != user.username:
                existing = User.query.filter_by(username=form.username.data).first()
                if existing:
                    flash('Это имя пользователя уже занято!', 'danger')
                    return redirect(url_for('admin.dashboard'))

            user_service.update_user(
                user=user,
                username=form.username.data,
                role=form.role.data,
                category_ids=form.category_ids.data,
                password=form.password.data,
            )
            logger.info(f'Admin {current_user.username} updated user: {user.username}')
            flash(f'Данные пользователя {user.username} успешно обновлены!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating user: {e}')
            flash(f'Ошибка при обновлении пользователя: {e}', 'danger')
    else:
        flash_form_errors(form)

    return render_template('admin/edit_user.html', user=user, form=form, categories=categories)


@admin_bp.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    _require_admin()

    user = User.query.get_or_404(user_id)
    user_service.delete_user(user)
    flash('Пользователь успешно удален', 'success')
    return redirect(url_for('admin.dashboard'))


# ─── Categories CRUD ─────────────────────────────────────────────

@admin_bp.route('/create_category', methods=['GET', 'POST'])
@login_required
def create_category():
    _require_admin()

    form = CategoryForm()
    if form.validate_on_submit():
        try:
            category_service.create_category(name=form.name.data)
            logger.info(f'Admin {current_user.username} created category: {form.name.data}')
            flash('Категория успешно создана!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error creating category: {e}')
            flash(f'Ошибка при создании категории: {e}', 'danger')
    else:
        flash_form_errors(form)

    return render_template('admin/partials/create_category_form.html', form=form)


@admin_bp.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    _require_admin()

    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)

    if request.method == 'GET':
        return render_template('admin/partials/edit_category_form.html', category=category, form=form)

    if form.validate_on_submit():
        try:
            if form.name.data != category.name:
                existing = Category.query.filter_by(name=form.name.data).first()
                if existing:
                    flash('Категория с таким названием уже существует!', 'danger')
                    return redirect(url_for('admin.dashboard'))
            category_service.update_category(category, name=form.name.data)
            logger.info(f'Admin {current_user.username} updated category: {category.name}')
            flash('Название категории успешно изменено!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating category: {e}')
            flash(f'Ошибка при обновлении категории: {e}', 'danger')
    else:
        flash_form_errors(form)

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/delete_category/<int:category_id>')
@login_required
def delete_category(category_id):
    _require_admin()

    category = Category.query.get_or_404(category_id)
    category_service.delete_category(category)
    flash('Категория успешно удалена', 'success')
    return redirect(url_for('admin.dashboard'))


# ─── QR Codes CRUD ───────────────────────────────────────────────

@admin_bp.route('/generate_qr', methods=['GET', 'POST'])
@login_required
def generate_qr():
    _require_admin()

    form = QRForm()

    if request.method == 'GET':
        form.logo_scale.data = 5

    users = User.query.all()
    form.user_id.choices = [(u.id, u.username) for u in users]
    categories = Category.query.all()
    form.category_ids.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        try:
            logo_file = request.files.get('logo_image')
            logo_data = logo_file.read() if logo_file and logo_file.filename else None

            qr_service.generate_qr_code(
                name=form.name.data,
                link=form.link.data,
                user_id=form.user_id.data,
                category_ids=form.category_ids.data,
                fill_color=form.fill_color.data,
                back_color=form.back_color.data,
                scale=form.scale.data,
                logo_image=logo_data,
                logo_scale=form.logo_scale.data,
            )
            logger.info(f'Admin {current_user.username} generated QR code: {form.name.data}')
            flash('Динамический QR-код успешно сгенерирован!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error generating QR code: {e}')
            flash(f'Ошибка при генерации QR-кода: {e}', 'danger')
    else:
        flash_form_errors(form)

    return render_template(
        'admin/partials/generate_qr_form.html',
        form=form,
        users=users,
        categories=categories,
    )


@admin_bp.route('/edit_qr/<int:qr_id>', methods=['GET', 'POST'])
@login_required
def edit_qr(qr_id):
    _require_admin()

    qr_entry = QRCode.query.get_or_404(qr_id)

    if qr_entry.logo_scale is None:
        qr_entry.logo_scale = 5

    form = EditQRForm(obj=qr_entry)

    users = User.query.all()
    form.user_id.choices = [(u.id, u.username) for u in users]
    categories = Category.query.all()
    form.category_ids.choices = [(c.id, c.name) for c in categories]

    if request.method == 'GET':
        qr_image_b64 = encode_image_base64(qr_entry.image_data)
        return render_template(
            'admin/partials/edit_qr_form.html',
            qr=qr_entry,
            qr_image_b64=qr_image_b64,
            form=form,
            users=users,
            categories=categories,
        )

    if form.validate_on_submit():
        if not validate_url(form.link.data):
            flash('Некорректная ссылка!', 'danger')
            return redirect(url_for('admin.dashboard'))

        try:
            logo_file = request.files.get('logo_image')
            logo_data = logo_file.read() if logo_file and logo_file.filename else None

            qr_service.update_qr_code(
                qr_entry=qr_entry,
                name=form.name.data,
                link=form.link.data,
                user_id=form.user_id.data,
                category_ids=form.category_ids.data,
                fill_color=form.fill_color.data,
                back_color=form.back_color.data,
                scale=form.scale.data,
                logo_image=logo_data,
                logo_scale=form.logo_scale.data,
            )
            logger.info(f'Admin {current_user.username} updated QR code: {qr_entry.name}')
            flash(f'QR-код с ID "{qr_entry.id}" успешно обновлен!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating QR code: {e}')
            flash(f'Ошибка при обновлении QR-кода: {e}', 'danger')
    else:
        flash('Ошибка в валидации данных!', 'danger')

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/download_qr/<int:qr_id>')
@login_required
def download_qr(qr_id):
    _require_admin()

    qr_entry = QRCode.query.get_or_404(qr_id)

    if not qr_entry.image_data:
        flash('Изображение QR-кода отсутствует!', 'danger')
        return redirect(url_for('admin.dashboard'))

    return send_file(
        io.BytesIO(qr_entry.image_data),
        mimetype='image/png',
        as_attachment=True,
        download_name=f'qr_user_{qr_entry.user_id}_{qr_entry.id}.png',
    )


@admin_bp.route('/delete_qr/<int:qr_id>')
@login_required
def delete_qr(qr_id):
    _require_admin()

    qr_entry = QRCode.query.get_or_404(qr_id)
    qr_service.delete_qr_code(qr_entry)
    flash('QR-код успешно удален', 'success')
    return redirect(url_for('admin.dashboard'))
