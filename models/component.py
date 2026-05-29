from database.db import db


class Component(db.Model):
    __bind_key__ = "components"
    __tablename__ = "components"

    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    brand    = db.Column(db.String(50),  nullable=False)
    category = db.Column(db.String(30),  nullable=False)
    price    = db.Column(db.Float,       nullable=False)
    specs    = db.Column(db.String(200), nullable=True)

    links = db.relationship("Link", backref="component", lazy=True)

    def to_dict(self):
        return {
            "id":       self.id,
            "name":     self.name,
            "brand":    self.brand,
            "category": self.category,
            "price":    self.price,
            "specs":    self.specs,
        }

    def __repr__(self):
        return f"<Component {self.name} ({self.category})>"
