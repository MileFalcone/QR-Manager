from app.extensions import db

qrcode_categories = db.Table('qrcode_categories',
    db.Column('qrcode_id', db.Integer, db.ForeignKey('qrcode.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

user_categories = db.Table('user_categories',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

from app.models.user import User
from app.models.qrcode import QRCode
from app.models.category import Category
from app.models.setting import Setting

__all__ = ['User', 'QRCode', 'Category', 'Setting', 'qrcode_categories', 'user_categories']
