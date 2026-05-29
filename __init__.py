import json
import os
from flask import Flask
from database.db import db
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.build_routes import build_bp
from routes.component_routes import component_bp
from routes.admin_routes import admin_bp


def _seed_components(app):
    from models.component import Component
    from models.link import Link

    if Component.query.first():
        return

    base = os.path.dirname(os.path.abspath(__file__))

    components_path = os.path.join(base, "data", "components.json")
    links_path      = os.path.join(base, "data", "links.json")

    if not os.path.exists(components_path):
        return

    with open(components_path) as f:
        components_data = json.load(f)

    for item in components_data:
        c = Component(
            id=item["id"],
            name=item["name"],
            brand=item["brand"],
            category=item["category"],
            price=item["price"],
            specs=item.get("specs", ""),
        )
        db.session.add(c)

    db.session.commit()

    if not os.path.exists(links_path):
        return

    with open(links_path) as f:
        links_data = json.load(f)

    for item in links_data:
        link = Link(
            component_id=item["component_id"],
            store_name=item["store_name"],
            url=item["url"],
            price=item["price"],
        )
        db.session.add(link)

    db.session.commit()


def _seed_admin():
    """Create a default admin account if none exists."""
    from models.user import User
    if not User.query.filter_by(is_admin=True).first():
        admin = User(username="admin", email="admin@buildlab.ph", is_admin=True)
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Default admin created: admin@buildlab.ph / admin123")


def create_app():
    app = Flask(__name__)

    # Secret key — use env var on Render, fallback for local
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "buildlab-secret-key-change-me")

    # Database — support Render's DATABASE_URL (PostgreSQL) or local SQLite
    database_url = os.environ.get("DATABASE_URL", "")
    # Render gives postgres:// but SQLAlchemy needs postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    if database_url:
        # Single DB on Render (PostgreSQL) — both models use same DB
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        app.config["SQLALCHEMY_BINDS"] = {
            "components": database_url
        }
    else:
        # Local SQLite
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
        app.config["SQLALCHEMY_BINDS"] = {
            "components": "sqlite:///components.db"
        }

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        _seed_components(app)
        _seed_admin()

    app.jinja_env.filters["from_json"] = json.loads

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(build_bp)
    app.register_blueprint(component_bp)
    app.register_blueprint(admin_bp)

    return app
