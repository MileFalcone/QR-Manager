from app.extensions import db


class QRCode(db.Model):
    __tablename__ = 'qrcode'

    __table_args__ = (
        db.Index('idx_user_created', 'user_id', 'created_at'),
        db.Index('idx_user_name', 'user_id', 'name'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(500), nullable=False)
    key = db.Column(db.String(50), unique=True, nullable=False, index=True)
    image_data = db.Column(db.LargeBinary, nullable=False)
    fill_color = db.Column(db.String(7), default='#000000')
    back_color = db.Column(db.String(7), default='#FFFFFF')
    scale = db.Column(db.Integer, default=10)
    logo_image = db.Column(db.LargeBinary, nullable=True)
    logo_scale = db.Column(db.Integer, default=5)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    categories = db.relationship('Category', secondary='qrcode_categories', lazy='subquery',
                                 backref=db.backref('qrcodes', lazy=True))

    def __repr__(self) -> str:
        return f'<QRCode {self.name}>'
