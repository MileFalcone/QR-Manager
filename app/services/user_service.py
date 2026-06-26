import logging

from app.extensions import db
from app.models import User, Category

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


def create_user(username: str, password: str, role: str = 'user',
                category_ids=None) -> User:
    """Create a new user with hashed password and optional category assignments."""
    user = User(username=username)
    user.set_password(password)
    user.role = role
    user.is_admin = (role == 'admin')
    selected = _resolve_categories(category_ids)
    user.categories.extend(selected)

    db.session.add(user)
    db.session.commit()
    logger.info(f'User created: {username}')
    return user


def update_user(user: User, username: str, role: str,
                category_ids, password: str | None = None) -> User:
    """Update user fields and optionally reset password."""
    user.username = username
    user.role = role
    user.is_admin = (role == 'admin')
    user.categories = _resolve_categories(category_ids)

    if password and password.strip():
        user.set_password(password)

    db.session.commit()
    logger.info(f'User updated: {user.username}')
    return user


def delete_user(user: User) -> None:
    """Delete a user record."""
    db.session.delete(user)
    db.session.commit()
    logger.info(f'User deleted: {user.id}')


def get_paginated_users(page: int = 1, per_page: int = 20):
    """Get paginated users."""
    return User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
