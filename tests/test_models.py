"""
Tests for all database models — CRUD operations and relationships.
Run with: python -m pytest tests/test_models.py -v
"""
import pytest
from app import create_app
from database.db import db
from models.component import Component
from models.link      import Link
from models.user      import User
from models.build     import Build


@pytest.fixture
def app():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


# ── Component model ────────────────────────────────────────────────────
class TestComponentModel:
    def test_create_component(self, app):
        with app.app_context():
            c = Component(name="RTX 4070", brand="NVIDIA", category="GPU",
                          price=36000, specs="12GB GDDR6X, 2475MHz")
            db.session.add(c)
            db.session.commit()
            assert c.id is not None

    def test_to_dict(self, app):
        with app.app_context():
            c = Component(name="RTX 4070", brand="NVIDIA", category="GPU", price=36000)
            db.session.add(c); db.session.commit()
            d = c.to_dict()
            assert d["name"] == "RTX 4070"
            assert d["price"] == 36000
            assert d["category"] == "GPU"

    def test_filter_by_category(self, app):
        with app.app_context():
            for name, cat in [("RTX 4070","GPU"),("RX 7600","GPU"),("i5-13600K","CPU")]:
                db.session.add(Component(name=name, brand="X", category=cat, price=10000))
            db.session.commit()
            gpus = Component.get_by_category("GPU")
            assert len(gpus) == 2

    def test_search_by_name(self, app):
        with app.app_context():
            db.session.add(Component(name="Core i9-13900K", brand="Intel", category="CPU", price=35000))
            db.session.add(Component(name="Core i5-13600K", brand="Intel", category="CPU", price=17500))
            db.session.commit()
            results = Component.search("i9")
            assert len(results) == 1
            assert results[0].name == "Core i9-13900K"

    def test_price_filter(self, app):
        with app.app_context():
            db.session.add(Component(name="Budget CPU", brand="AMD", category="CPU", price=10000))
            db.session.add(Component(name="Mid CPU",    brand="AMD", category="CPU", price=20000))
            db.session.add(Component(name="High CPU",   brand="AMD", category="CPU", price=40000))
            db.session.commit()
            results = Component.filter_by_price(max_price=25000)
            assert all(c.price <= 25000 for c in results)
            assert len(results) == 2


# ── Link model ────────────────────────────────────────────────────────
class TestLinkModel:
    def test_create_link(self, app):
        with app.app_context():
            c = Component(name="RTX 4070", brand="NVIDIA", category="GPU", price=36000)
            db.session.add(c); db.session.commit()
            link = Link(component_id=c.id, store_name="Shopee",
                        price=35900, url="https://shopee.ph/rtx4070")
            db.session.add(link); db.session.commit()
            assert link.id is not None
            assert link.component_id == c.id

    def test_component_link_relationship(self, app):
        with app.app_context():
            c = Component(name="RX 7600", brand="AMD", category="GPU", price=18000)
            db.session.add(c); db.session.commit()
            for store, price in [("Shopee", 17800), ("Lazada", 18200), ("PC Express", 18500)]:
                db.session.add(Link(component_id=c.id, store_name=store, price=price, url="http://x"))
            db.session.commit()
            assert len(c.links) == 3

    def test_cheapest_link(self, app):
        with app.app_context():
            c = Component(name="GPU X", brand="Y", category="GPU", price=20000)
            db.session.add(c); db.session.commit()
            db.session.add(Link(component_id=c.id, store_name="A", price=19500, url="http://a"))
            db.session.add(Link(component_id=c.id, store_name="B", price=20500, url="http://b"))
            db.session.commit()
            cheapest = Link.get_cheapest(c.id)
            assert cheapest.price == 19500


# ── User model ────────────────────────────────────────────────────────
class TestUserModel:
    def test_create_user(self, app):
        with app.app_context():
            u = User(username="testuser", email="test@buildlab.ph")
            u.set_password("secret123")
            db.session.add(u); db.session.commit()
            assert u.id is not None

    def test_password_hash(self, app):
        with app.app_context():
            u = User(username="hashtest", email="hash@buildlab.ph")
            u.set_password("mypassword")
            db.session.add(u); db.session.commit()
            assert u.check_password("mypassword") is True
            assert u.check_password("wrongpass") is False

    def test_unique_email(self, app):
        with app.app_context():
            u1 = User(username="user1", email="dup@buildlab.ph")
            u1.set_password("pass")
            u2 = User(username="user2", email="dup@buildlab.ph")
            u2.set_password("pass")
            db.session.add(u1); db.session.commit()
            db.session.add(u2)
            with pytest.raises(Exception):
                db.session.commit()


# ── Build model ───────────────────────────────────────────────────────
class TestBuildModel:
    def test_create_build(self, app):
        with app.app_context():
            u = User(username="builder", email="b@buildlab.ph"); u.set_password("x")
            c = Component(name="RTX 4080", brand="NVIDIA", category="GPU", price=68000)
            db.session.add_all([u, c]); db.session.commit()
            build = Build(user_id=u.id, name="My Gaming Rig")
            build.components.append(c)
            db.session.add(build); db.session.commit()
            assert build.id is not None
            assert len(build.components) == 1

    def test_build_total(self, app):
        with app.app_context():
            u = User(username="b2", email="b2@buildlab.ph"); u.set_password("x")
            c1 = Component(name="CPU X", brand="A", category="CPU", price=16000)
            c2 = Component(name="GPU Y", brand="B", category="GPU", price=36000)
            db.session.add_all([u, c1, c2]); db.session.commit()
            build = Build(user_id=u.id, name="Budget Build")
            build.components.extend([c1, c2])
            db.session.add(build); db.session.commit()
            assert build.total_price == 52000

    def test_user_builds_relationship(self, app):
        with app.app_context():
            u = User(username="b3", email="b3@buildlab.ph"); u.set_password("x")
            db.session.add(u); db.session.commit()
            for n in ["Build A", "Build B"]:
                db.session.add(Build(user_id=u.id, name=n))
            db.session.commit()
            assert len(u.builds) == 2
