from flask import Blueprint, render_template, request, jsonify
from models.component import Component
from models.link import Link

component_bp = Blueprint("components", __name__)


@component_bp.route("/parts")
def parts():
    category = request.args.get("category", "")
    search   = request.args.get("search", "")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)

    query = Component.query
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(
            (Component.name.ilike(f"%{search}%")) |
            (Component.brand.ilike(f"%{search}%"))
        )
    if min_price is not None:
        query = query.filter(Component.price >= min_price)
    if max_price is not None:
        query = query.filter(Component.price <= max_price)

    components = query.order_by(Component.category, Component.price).all()
    categories = sorted(set(c.category for c in Component.query.all()))
    return render_template("parts.html", components=components, categories=categories,
                           active_category=category, search=search)


@component_bp.route("/api/components")
def api_components():
    category  = request.args.get("category", "")
    search    = request.args.get("search", "")
    query = Component.query
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Component.name.ilike(f"%{search}%"))
    return jsonify([c.to_dict() for c in query.all()])


@component_bp.route("/api/components/<int:component_id>/links")
def component_links(component_id):
    links = Link.query.filter_by(component_id=component_id).all()
    return jsonify([l.to_dict() for l in links])
