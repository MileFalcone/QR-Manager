from app.extensions import db


class Setting(db.Model):
    __tablename__ = 'setting'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.String(500), nullable=False, default='')

    @classmethod
    def get(cls, key, default=''):
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default

    @classmethod
    def set(cls, key, value):
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = cls(key=key, value=value)
            db.session.add(setting)
        db.session.commit()
        return setting

    @classmethod
    def get_all(cls):
        settings = cls.query.all()
        return {s.key: s.value for s in settings}

    def __repr__(self):
        return f'<Setting {self.key}={self.value}>'
