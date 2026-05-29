from database.db import db

class Storage(db.Model):
    __tablename__ = "storage_devices"

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    brand         = db.Column(db.String(60), nullable=False)
    price         = db.Column(db.Integer, nullable=False)
    capacity_gb   = db.Column(db.Integer)       # 500, 1000, 2000
    storage_type  = db.Column(db.String(20))    # NVMe, SATA SSD, HDD
    interface     = db.Column(db.String(20))    # PCIe 4.0, PCIe 3.0, SATA
    read_speed    = db.Column(db.Integer)       # MB/s
    write_speed   = db.Column(db.Integer)       # MB/s
    form_factor   = db.Column(db.String(20))    # M.2 2280, 2.5"
    component_id  = db.Column(db.Integer, db.ForeignKey("components.id"), nullable=False)
    component     = db.relationship("Component", backref=db.backref("storage_detail", uselist=False))

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "brand": self.brand,
            "price": self.price, "capacity_gb": self.capacity_gb,
            "storage_type": self.storage_type, "interface": self.interface,
            "read_speed": self.read_speed, "write_speed": self.write_speed,
        }

    @staticmethod
    def get_all():
        return Storage.query.order_by(Storage.price).all()

    @staticmethod
    def get_nvme():
        return Storage.query.filter_by(storage_type="NVMe").order_by(Storage.read_speed.desc()).all()
