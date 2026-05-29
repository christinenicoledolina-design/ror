from database.db import db
from datetime import datetime

# Association table for many-to-many Build <-> Component
build_components = db.Table(
    "build_components",
    db.Column("build_id",     db.Integer, db.ForeignKey("builds.id")),
    db.Column("component_id", db.Integer),
)


class Build(db.Model):
    __tablename__ = "builds"

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False, default="My Build")
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Store component IDs as JSON string (simple approach)
    component_ids = db.Column(db.Text, nullable=False, default="[]")

    def __repr__(self):
        return f"<Build {self.name} by User#{self.user_id}>"
