from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_
from werkzeug.utils import secure_filename
import os
import uuid

from extensions import db
from models import Customer, Item, CompanySettings, Quotation, WorkOrder

main_bp = Blueprint("main", __name__)

ALLOWED_LOGO_EXT = {"png", "jpg", "jpeg", "gif", "webp"}


@main_bp.route("/")
@login_required
def dashboard():
    recent_quotations = Quotation.query.order_by(Quotation.created_at.desc()).limit(8).all()
    recent_wos = WorkOrder.query.order_by(WorkOrder.created_at.desc()).limit(8).all()
    stats = {
        "quotations_total": Quotation.query.count(),
        "quotations_draft": Quotation.query.filter_by(status="Draft").count(),
        "quotations_sent": Quotation.query.filter_by(status="Sent").count(),
        "quotations_confirmed": Quotation.query.filter_by(status="Confirmed").count(),
        "work_orders_open": WorkOrder.query.filter(WorkOrder.status != "Completed").count(),
    }
    return render_template("dashboard.html", recent_quotations=recent_quotations,
                            recent_wos=recent_wos, stats=stats)


# ---------------- Customers ----------------

@main_bp.route("/customers")
@login_required
def customers():
    q = request.args.get("q", "").strip()
    query = Customer.query
    if q:
        query = query.filter(Customer.name.ilike(f"%{q}%"))
    all_customers = query.order_by(Customer.name).all()
    return render_template("customers.html", customers=all_customers, q=q)


@main_bp.route("/customers/new", methods=["GET", "POST"])
@login_required
def new_customer():
    if request.method == "POST":
        c = Customer(
            name=request.form.get("name", "").strip(),
            address=request.form.get("address", "").strip(),
            state=request.form.get("state", "").strip(),
            gst_no=request.form.get("gst_no", "").strip(),
            kind_attention=request.form.get("kind_attention", "").strip(),
            email=request.form.get("email", "").strip(),
        )
        db.session.add(c)
        db.session.commit()
        flash(f"Customer '{c.name}' saved.", "success")
        next_url = request.args.get("next")
        return redirect(next_url or url_for("main.customers"))
    return render_template("customer_form.html")


# ---------------- JSON APIs used by the quotation form (dropdowns / autocomplete) ----------------

@main_bp.route("/api/customers")
@login_required
def api_customers():
    customers = Customer.query.order_by(Customer.name).all()
    return jsonify([
        {"id": c.id, "name": c.name, "address": c.address, "state": c.state,
         "gst_no": c.gst_no, "kind_attention": c.kind_attention, "email": c.email}
        for c in customers
    ])


@main_bp.route("/api/items")
@login_required
def api_items():
    q = request.args.get("q", "").strip()
    query = Item.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Item.description.ilike(like), Item.item_code.ilike(like)))
    items = query.limit(25).all()
    return jsonify([
        {"id": i.id, "item_code": i.item_code, "description": i.description,
         "unit": i.unit, "rate": i.rate, "pcr_rate": i.pcr_rate,
         "suggested_price": i.pcr_rate if i.pcr_rate else i.rate}
        for i in items
    ])


# ---------------- Company settings ----------------

@main_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if not current_user.is_admin:
        flash("Only admins can edit company settings.", "danger")
        return redirect(url_for("main.dashboard"))

    s = db.session.get(CompanySettings, 1)
    if request.method == "POST":
        for field in ["company_name", "address_line", "state", "gst_no", "pan_no", "cin_no",
                      "telephone", "bank_name", "bank_account_no", "bank_ifsc", "bank_branch",
                      "quotation_prefix", "default_scope", "default_taxes", "default_payment_terms",
                      "default_delivery_period", "default_packing_charges", "default_warranty_terms",
                      "default_price_validity"]:
            setattr(s, field, request.form.get(field, getattr(s, field)))

        logo_file = request.files.get("logo")
        if logo_file and logo_file.filename:
            ext = logo_file.filename.rsplit(".", 1)[-1].lower()
            if ext in ALLOWED_LOGO_EXT:
                filename = f"logo_{uuid.uuid4().hex[:8]}.{ext}"
                logo_file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
                s.logo_filename = filename
            else:
                flash("Logo must be a PNG, JPG, GIF or WEBP image.", "danger")

        db.session.commit()
        flash("Company settings updated.", "success")
        return redirect(url_for("main.settings"))

    return render_template("settings.html", s=s)
