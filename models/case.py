from database.db import db

class Case(db.Model):
    __tablename__ = "cases"

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(120), nullable=False)
    brand           = db.Column(db.String(60), nullable=False)
    price           = db.Column(db.Integer, nullable=False)
    form_factor     = db.Column(db.String(20))   # ATX, mATX, ITX, Full Tower
    max_gpu_length  = db.Column(db.Integer)       # mm
    max_cpu_height  = db.Column(db.Integer)       # mm
    max_radiator    = db.Column(db.Integer)       # mm
    drive_bays_35   = db.Column(db.Integer)
    drive_bays_25   = db.Column(db.Integer)
    included_fans   = db.Column(db.Integer)
    has_rgb         = db.Column(db.Boolean, default=False)
    panel_type      = db.Column(db.String(30))   # Mesh, Tempered Glass
    component_id    = db.Column(db.Integer, db.ForeignKey("components.id"), nullable=False)
    component       = db.relationship("Component", backref=db.backref("case_detail", uselist=False))

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "brand": self.brand,
            "price": self.price, "form_factor": self.form_factor,
            "max_gpu_length": self.max_gpu_length, "max_cpu_height": self.max_cpu_height,
            "max_radiator": self.max_radiator, "panel_type": self.panel_type,
        }

    @staticmethod
    def get_all():
        return Case.query.order_by(Case.price).all()

    @staticmethod
    def get_compatible_with_gpu(gpu_length_mm: int):
        return Case.query.filter(Case.max_gpu_length >= gpu_length_mm).order_by(Case.price).all()
