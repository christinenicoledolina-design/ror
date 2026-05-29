from database.db import db


class Link(db.Model):
    __bind_key__ = "components"
    __tablename__ = "links"

    id           = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey("components.id"), nullable=False)
    store_name   = db.Column(db.String(50),  nullable=False)
    url          = db.Column(db.String(300), nullable=False)
    price        = db.Column(db.Float,       nullable=False)

    def to_dict(self):
        return {
            "id":         self.id,
            "store_name": self.store_name,
            "url":        self.url,
            "price":      self.price,
        }
