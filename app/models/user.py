from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import subqueryload

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    categories = db.relationship('Category', secondary='user_categories', lazy='subquery',
                                 backref=db.backref('users', lazy=True))
    qrcodes = db.relationship('QRCode', backref='owner', lazy='dynamic')

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def get_shared_qrcodes(self):
        """Get all QR codes from categories the user has access to.

        Uses eager loading (subqueryload) to avoid N+1 queries
        when iterating over qr.categories.
        """
        return QRCode.query.join(QRCode.categories)\
                           .join(Category.users)\
                           .filter(User.id == self.id)\
                           .options(subqueryload(QRCode.categories))\
                           .distinct()

    def __repr__(self) -> str:
        return f'<User {self.username}>'


# Avoid circular import by importing at end of module
from app.models.qrcode import QRCode
from app.models.category import Category
