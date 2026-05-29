from database.db import db
from models.component import Component

class CPU(db.Model):
    __tablename__ = "cpus"

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(120), nullable=False)
    brand      = db.Column(db.String(60), nullable=False)
    price      = db.Column(db.Integer, nullable=False)
    cores      = db.Column(db.Integer)
    threads    = db.Column(db.Integer)
    base_clock = db.Column(db.Float)          # GHz
    boost_clock= db.Column(db.Float)          # GHz
    tdp        = db.Column(db.Integer)        # Watts
    socket     = db.Column(db.String(30))     # e.g. LGA1700, AM5
    memory_type= db.Column(db.String(20))     # DDR4 / DDR5
    component_id = db.Column(db.Integer, db.ForeignKey("components.id"), nullable=False)
    component  = db.relationship("Component", backref=db.backref("cpu_detail", uselist=False))

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "brand": self.brand,
            "price": self.price, "cores": self.cores, "threads": self.threads,
            "base_clock": self.base_clock, "boost_clock": self.boost_clock,
            "tdp": self.tdp, "socket": self.socket, "memory_type": self.memory_type,
        }

    @staticmethod
    def get_all():
        return CPU.query.order_by(CPU.price).all()

    @staticmethod
    def get_by_socket(socket: str):
        return CPU.query.filter_by(socket=socket).all()

    @staticmethod
    def get_by_id(cpu_id: int):
        return CPU.query.get_or_404(cpu_id)

    @staticmethod
    def filter_by_price(max_price: int):
        return CPU.query.filter(CPU.price <= max_price).order_by(CPU.price).all()
