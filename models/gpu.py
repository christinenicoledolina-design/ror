from database.db import db

class GPU(db.Model):
    __tablename__ = "gpus"

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(120), nullable=False)
    brand        = db.Column(db.String(60), nullable=False)
    price        = db.Column(db.Integer, nullable=False)
    vram_gb      = db.Column(db.Integer)
    memory_type  = db.Column(db.String(20))   # GDDR6, GDDR6X
    boost_clock  = db.Column(db.Integer)      # MHz
    tdp          = db.Column(db.Integer)      # Watts
    pcie_slot    = db.Column(db.String(20))   # PCIe 4.0 x16
    component_id = db.Column(db.Integer, db.ForeignKey("components.id"), nullable=False)
    component    = db.relationship("Component", backref=db.backref("gpu_detail", uselist=False))

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "brand": self.brand,
            "price": self.price, "vram_gb": self.vram_gb,
            "memory_type": self.memory_type, "boost_clock": self.boost_clock,
            "tdp": self.tdp, "pcie_slot": self.pcie_slot,
        }

    @staticmethod
    def get_all():
        return GPU.query.order_by(GPU.price).all()

    @staticmethod
    def get_by_id(gpu_id: int):
        return GPU.query.get_or_404(gpu_id)

    @staticmethod
    def filter_by_vram(min_vram: int):
        return GPU.query.filter(GPU.vram_gb >= min_vram).order_by(GPU.price).all()
