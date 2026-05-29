import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify, Response
from database.db import db
from models.build import Build
from models.component import Component
from models.user import User
from services.compatibility_service import check_compatibility

build_bp = Blueprint("build", __name__)


@build_bp.route("/builder")
def builder():
    from sqlalchemy.orm import joinedload
    components = Component.query.options(joinedload(Component.links)).order_by(Component.category).all()
    categories = sorted(set(c.category for c in components))
    return render_template("builder/builder.html", components=components, categories=categories)


@build_bp.route("/builds")
def saved_builds():
    if "user_id" not in session:
        flash("Please log in to view your builds.", "warning")
        return redirect(url_for("auth.login"))
    user   = User.query.get(session["user_id"])
    builds = Build.query.filter_by(user_id=session["user_id"]).order_by(Build.created_at.desc()).all()

    total_spend = 0
    total_parts = 0
    for b in builds:
        ids = json.loads(b.component_ids)
        total_parts += len(ids)
        comps = Component.query.filter(Component.id.in_(ids)).all()
        total_spend += sum(c.price for c in comps)

    avg_cost = total_spend / len(builds) if builds else 0

    return render_template(
        "builder/saved_builds.html",
        user=user,
        builds=builds,
        total_spend=total_spend,
        avg_cost=avg_cost,
        total_parts=total_parts,
    )


@build_bp.route("/api/builds/save", methods=["POST"])
def save_build():
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    data          = request.get_json()
    name          = data.get("name", "My Build")
    component_ids = data.get("component_ids", [])
    build = Build(
        name=name,
        user_id=session["user_id"],
        component_ids=json.dumps(component_ids),
    )
    db.session.add(build)
    db.session.commit()
    return jsonify({"message": "Build saved!", "id": build.id})


@build_bp.route("/api/builds/<int:build_id>", methods=["DELETE"])
def delete_build(build_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    build = Build.query.filter_by(id=build_id, user_id=session["user_id"]).first()
    if not build:
        return jsonify({"error": "Build not found"}), 404
    db.session.delete(build)
    db.session.commit()
    return jsonify({"message": "Build deleted."})


@build_bp.route("/api/builds/<int:build_id>/rename", methods=["PATCH"])
def rename_build(build_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    build = Build.query.filter_by(id=build_id, user_id=session["user_id"]).first()
    if not build:
        return jsonify({"error": "Build not found"}), 404
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name cannot be empty"}), 400
    build.name = name
    db.session.commit()
    return jsonify({"message": "Build renamed.", "name": build.name})


@build_bp.route("/builds/<int:build_id>/export")
def export_build(build_id):
    if "user_id" not in session:
        flash("Please log in to export builds.", "warning")
        return redirect(url_for("auth.login"))
    build = Build.query.filter_by(id=build_id, user_id=session["user_id"]).first()
    if not build:
        flash("Build not found.", "danger")
        return redirect(url_for("build.saved_builds"))

    component_ids = json.loads(build.component_ids)
    components    = Component.query.filter(Component.id.in_(component_ids)).all()
    comp_map      = {c.id: c for c in components}

    lines = []
    lines.append(f"BuildLab — {build.name}")
    lines.append(f"Saved: {build.created_at.strftime('%B %d, %Y')}")
    lines.append("=" * 40)

    total = 0
    for cid in component_ids:
        c = comp_map.get(cid)
        if c:
            lines.append(f"{c.category:<14} {c.name} ({c.brand})  —  P{c.price:,.0f}")
            total += c.price

    lines.append("=" * 40)
    lines.append(f"{'TOTAL':<14} P{total:,.0f}")

    content  = "\n".join(lines)
    filename = build.name.replace(" ", "_") + ".txt"
    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@build_bp.route("/api/compatibility", methods=["POST"])
def compatibility():
    data          = request.get_json()
    component_ids = data.get("component_ids", [])
    components    = Component.query.filter(Component.id.in_(component_ids)).all()
    result        = check_compatibility(components)
    return jsonify(result)
