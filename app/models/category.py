from app.extensions import db


class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self) -> str:
        return f'<Category {self.name}>'
