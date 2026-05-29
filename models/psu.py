from database.db import db

class PSU(db.Model):
    __tablename__ = "psus"

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(120), nullable=False)
    brand        = db.Column(db.String(60), nullable=False)
    price        = db.Column(db.Integer, nullable=False)
    wattage      = db.Column(db.Integer)      # 650, 750, 850 …
    efficiency   = db.Column(db.String(20))   # 80+ Gold, Platinum
    modular      = db.Column(db.String(20))   # Full, Semi, None
    form_factor  = db.Column(db.String(20))   # ATX, SFX
    component_id = db.Column(db.Integer, db.ForeignKey("components.id"), nullable=False)
    component    = db.relationship("Component", backref=db.backref("psu_detail", uselist=False))

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "brand": self.brand,
            "price": self.price, "wattage": self.wattage,
            "efficiency": self.efficiency, "modular": self.modular,
        }

    @staticmethod
    def get_all():
        return PSU.query.order_by(PSU.wattage).all()

    @staticmethod
    def get_sufficient(required_watts: int):
        """Return PSUs with at least 20% headroom over required wattage."""
        min_watts = int(required_watts * 1.2)
        return PSU.query.filter(PSU.wattage >= min_watts).order_by(PSU.wattage).all()
