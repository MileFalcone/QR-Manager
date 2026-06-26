import os
import logging

from flask import Flask, redirect, url_for
from flask_login import current_user
from flask_cors import CORS

from app.config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):
    """Application factory.

    Creates and configures the Flask application with all
    extensions, blueprints, error handlers, and CLI commands.
    """
    root_dir = os.path.dirname(os.path.dirname(__file__))
    templates_dir = os.path.join(root_dir, 'templates')
    static_dir = os.path.join(root_dir, 'static')
    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
    app.config.from_object(config_class)

    # ── Logging ───────────────────────────────────────────────
    logging.basicConfig(level=logging.INFO)

    # ── Extensions ────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    CORS(app)

    # ── Inject settings into all templates ────────────────────
    from app.models import Setting

    @app.context_processor
    def inject_settings():
        return {'settings': Setting.get_all()}

    # ── AJAX redirect support ─────────────────────────────────
    from flask import request, jsonify

    @app.after_request
    def ajax_redirect(response):
        if (request.headers.get('X-Requested-With') == 'XMLHttpRequest'
                and response.status_code == 302):
            return jsonify({'redirect': response.location})
        return response

    # ── Error handlers ────────────────────────────────────────
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    # ── CLI commands ──────────────────────────────────────────
    from app.cli import register_commands
    register_commands(app)

    # ── Blueprints ────────────────────────────────────────────
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app
