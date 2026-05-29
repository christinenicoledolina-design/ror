from database.db import db

class Motherboard(db.Model):
    __tablename__ = "motherboards"

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(120), nullable=False)
    brand        = db.Column(db.String(60), nullable=False)
    price        = db.Column(db.Integer, nullable=False)
    socket       = db.Column(db.String(30))   # LGA1700, AM5
    chipset      = db.Column(db.String(30))   # Z790, X670E
    form_factor  = db.Column(db.String(20))   # ATX, mATX, ITX
    memory_type  = db.Column(db.String(10))   # DDR4, DDR5
    memory_slots = db.Column(db.Integer)
    max_memory   = db.Column(db.Integer)      # GB
    pcie_version = db.Column(db.String(10))   # PCIe 5.0
    wifi         = db.Column(db.Boolean, default=False)
    component_id = db.Column(db.Integer, db.ForeignKey("components.id"), nullable=False)
    component    = db.relationship("Component", backref=db.backref("mb_detail", uselist=False))

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "brand": self.brand,
            "price": self.price, "socket": self.socket, "chipset": self.chipset,
            "form_factor": self.form_factor, "memory_type": self.memory_type,
            "memory_slots": self.memory_slots, "max_memory": self.max_memory,
            "pcie_version": self.pcie_version, "wifi": self.wifi,
        }

    @staticmethod
    def get_all():
        return Motherboard.query.order_by(Motherboard.price).all()

    @staticmethod
    def get_by_socket(socket: str):
        return Motherboard.query.filter_by(socket=socket).all()

    @staticmethod
    def get_compatible(cpu_socket: str, memory_type: str):
        return Motherboard.query.filter_by(socket=cpu_socket, memory_type=memory_type).all()
