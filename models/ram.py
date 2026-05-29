from database.db import db

class RAM(db.Model):
    __tablename__ = "rams"

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(120), nullable=False)
    brand        = db.Column(db.String(60), nullable=False)
    price        = db.Column(db.Integer, nullable=False)
    capacity_gb  = db.Column(db.Integer)      # 8, 16, 32, 64
    speed_mhz    = db.Column(db.Integer)      # 3200, 5600 …
    memory_type  = db.Column(db.String(10))   # DDR4, DDR5
    kit_count    = db.Column(db.Integer)      # 1, 2, 4 (sticks)
    cas_latency  = db.Column(db.Integer)
    component_id = db.Column(db.Integer, db.ForeignKey("components.id"), nullable=False)
    component    = db.relationship("Component", backref=db.backref("ram_detail", uselist=False))

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "brand": self.brand,
            "price": self.price, "capacity_gb": self.capacity_gb,
            "speed_mhz": self.speed_mhz, "memory_type": self.memory_type,
            "kit_count": self.kit_count, "cas_latency": self.cas_latency,
        }

    @staticmethod
    def get_all():
        return RAM.query.order_by(RAM.price).all()

    @staticmethod
    def get_by_type(memory_type: str):
        return RAM.query.filter_by(memory_type=memory_type).all()
