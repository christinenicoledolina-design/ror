"""
test_components.py — Unit tests for component model and queries.
Run: python -m pytest tests/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from __init__ import create_app
from database.db import db as _db
from models.component import Component


@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_BINDS"] = {"components": "sqlite:///:memory:"}
    with app.app_context():
        _db.create_all()
        # Seed test data
        c1 = Component(name="Test CPU", brand="Intel", category="CPU", price=20000, specs="8 cores")
        c2 = Component(name="Test GPU", brand="NVIDIA", category="GPU", price=35000, specs="8GB")
        _db.session.add_all([c1, c2])
        _db.session.commit()
        yield app


def test_component_count(app):
    with app.app_context():
        assert Component.query.count() == 2


def test_filter_by_category(app):
    with app.app_context():
        cpus = Component.query.filter_by(category="CPU").all()
        assert len(cpus) == 1
        assert cpus[0].name == "Test CPU"


def test_price_filter(app):
    with app.app_context():
        cheap = Component.query.filter(Component.price < 25000).all()
        assert len(cheap) == 1
        assert cheap[0].brand == "Intel"


def test_to_dict(app):
    with app.app_context():
        c = Component.query.first()
        d = c.to_dict()
        assert "name" in d
        assert "price" in d
        assert "category" in d


def test_compatibility_service(app):
    from services.compatibility_service import check_compatibility
    with app.app_context():
        components = Component.query.all()
        result = check_compatibility(components)
        assert "compatible" in result
        assert "issues" in result
        assert isinstance(result["issues"], list)
