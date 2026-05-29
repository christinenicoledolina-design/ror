from database.db import db

class Cooling(db.Model):
    __tablename__ = "cooling"

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    brand         = db.Column(db.String(60), nullable=False)
    price         = db.Column(db.Integer, nullable=False)
    cooling_type  = db.Column(db.String(20))   # Air, AIO, Custom Loop
    radiator_size = db.Column(db.Integer)       # mm: 120, 240, 280, 360
    fan_count     = db.Column(db.Integer)
    fan_size_mm   = db.Column(db.Integer)       # 120, 140
    tdp_rating    = db.Column(db.Integer)       # Max TDP supported (W)
    height_mm     = db.Column(db.Integer)       # for air coolers
    component_id  = db.Column(db.Integer, db.ForeignKey("components.id"), nullable=False)
    component     = db.relationship("Component", backref=db.backref("cooling_detail", uselist=False))

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "brand": self.brand,
            "price": self.price, "cooling_type": self.cooling_type,
            "radiator_size": self.radiator_size, "fan_count": self.fan_count,
            "tdp_rating": self.tdp_rating,
        }

    @staticmethod
    def get_all():
        return Cooling.query.order_by(Cooling.price).all()

    @staticmethod
    def get_for_tdp(cpu_tdp: int):
        return Cooling.query.filter(Cooling.tdp_rating >= cpu_tdp).order_by(Cooling.price).all()
