import logging
from flask import render_template
from app.extensions import db

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register custom HTTP error pages."""

    @app.errorhandler(404)
    def not_found(error):
        return render_template('error/404.html'), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('error/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        logger.error(f'Internal Server Error: {error}')
        return render_template('error/500.html'), 500
