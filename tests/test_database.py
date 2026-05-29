"""
test_database.py — Tests for database setup and user model.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from __init__ import create_app
from database.db import db as _db
from models.user import User
from models.build import Build


@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_BINDS"] = {"components": "sqlite:///:memory:"}
    with app.app_context():
        _db.create_all()
        yield app


def test_create_user(app):
    with app.app_context():
        u = User(username="tester", email="test@buildlab.ph")
        u.set_password("password123")
        _db.session.add(u)
        _db.session.commit()
        assert User.query.filter_by(email="test@buildlab.ph").first() is not None


def test_password_check(app):
    with app.app_context():
        u = User.query.filter_by(username="tester").first()
        assert u.check_password("password123") is True
        assert u.check_password("wrongpass") is False


def test_save_build(app):
    with app.app_context():
        import json
        u = User.query.filter_by(username="tester").first()
        b = Build(name="My Test Build", user_id=u.id, component_ids=json.dumps([1, 2, 3]))
        _db.session.add(b)
        _db.session.commit()
        builds = Build.query.filter_by(user_id=u.id).all()
        assert len(builds) == 1
        assert builds[0].name == "My Test Build"
