"""
Reads components.json and links.json and inserts them into the database.
Run after create_db.py:
    python data/update_db.py
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from __init__ import create_app
from database.db import db
from models.component import Component
from models.link import Link

app = create_app()

with app.app_context():
    # Load components
    with open("data/components.json") as f:
        components_data = json.load(f)

    Component.query.delete()
    Link.query.delete()

    for item in components_data:
        c = Component(
            id=item["id"],
            name=item["name"],
            brand=item["brand"],
            category=item["category"],
            price=item["price"],
            specs=item.get("specs", ""),
        )
        db.session.add(c)

    db.session.commit()

    # Load links
    with open("data/links.json") as f:
        links_data = json.load(f)

    for item in links_data:
        link = Link(
            component_id=item["component_id"],
            store_name=item["store_name"],
            url=item["url"],
            price=item["price"],
        )
        db.session.add(link)

    db.session.commit()
    print(f"Imported {len(components_data)} components and {len(links_data)} links.")
