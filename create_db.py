"""
Run this once to create the database tables.
Usage: python create_db.py
"""
from __init__ import create_app
from database.db import db

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created successfully.")
    print("Run: python data/update_db.py  — to populate components")
