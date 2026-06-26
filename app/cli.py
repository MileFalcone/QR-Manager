import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models import User, Category, Setting


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database with test data."""
    db.create_all()

    _migrate_qrcode_table()
    _seed_settings()

    try:
        if not Category.query.filter_by(name='Работа').first():
            db.session.add(Category(name='Работа'))
        if not Category.query.filter_by(name='Личное').first():
            db.session.add(Category(name='Личное'))

        if not User.query.filter_by(username='user').first():
            user = User(username='user')
            user.set_password('user123')
            user.is_admin = False
            user.role = 'user'
            db.session.add(user)

        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('admin123')
            admin.is_admin = True
            admin.role = 'admin'
            db.session.add(admin)

        if not User.query.filter_by(username='moderator').first():
            moderator = User(username='moderator')
            moderator.set_password('moder123')
            moderator.is_admin = False
            moderator.role = 'moderator'
            db.session.add(moderator)

        db.session.commit()
        click.echo('Database initialized successfully!')
        click.echo('Test users:')
        click.echo('  - user / user123 (regular user)')
        click.echo('  - admin / admin123 (administrator)')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error initializing database: {e}', err=True)


def _migrate_qrcode_table():
    """Add missing columns to existing tables."""
    from flask import current_app
    import sqlite3, os

    db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
    if not db_path:
        return
    db_abs = os.path.join(current_app.instance_path, db_path) if not os.path.isabs(db_path) else db_path
    if not os.path.exists(db_abs):
        return

    try:
        conn = sqlite3.connect(db_abs)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in c.fetchall()}

        if 'qrcode' in tables:
            c.execute('PRAGMA table_info(qrcode)')
            cols = {r[1] for r in c.fetchall()}
            for col, col_type, default in [
                ('logo_image', 'BLOB', None),
                ('logo_scale', 'INTEGER', '5'),
            ]:
                if col not in cols:
                    default_clause = f"DEFAULT {default}" if default is not None else ""
                    c.execute(f"ALTER TABLE qrcode ADD COLUMN {col} {col_type} {default_clause}")
                    click.echo(f'  Added column: {col}')

        if 'user' in tables:
            c.execute('PRAGMA table_info(user)')
            cols = {r[1] for r in c.fetchall()}
            if 'role' not in cols:
                c.execute("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'user'")
                c.execute("UPDATE user SET role='admin' WHERE is_admin=1")
                c.execute("UPDATE user SET role='user' WHERE is_admin=0")
                click.echo('  Added column: role (user table)')

        conn.commit()
        conn.close()
    except Exception as e:
        click.echo(f'Warning: migration failed: {e}', err=True)


def _seed_settings():
    """Seed default settings into the setting table."""
    defaults = {
        'sitename': 'QR Manager',
        'version': 'v2.0',
    }
    for key, value in defaults.items():
        if not Setting.query.filter_by(key=key).first():
            db.session.add(Setting(key=key, value=value))
            click.echo(f'  Added setting: {key}={value}')


def register_commands(app):
    """Register Flask CLI commands."""
    app.cli.add_command(init_db_command)
