import json
from datetime import datetime, date

from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from flask_login import login_required, current_user

from extensions import db
from models import Quotation, QuotationItem, Customer, CompanySettings
from numbering import next_quotation_no
from utils.pdf_generator import build_quotation_pdf

quotations_bp = Blueprint("quotations", __name__, url_prefix="/quotations")


@quotations_bp.route("/")
@login_required
def list_quotations():
    status = request.args.get("status", "")
    query = Quotation.query
    if status:
        query = query.filter_by(status=status)
    quotations = query.order_by(Quotation.created_at.desc()).all()
    return render_template("quotation_list.html", quotations=quotations, status=status)


def _parse_items_from_form(form):
    sr_nos = form.getlist("sr_no[]")
    reqs = form.getlist("customer_requirement[]")
    codes = form.getlist("sql_code[]")
    qtys = form.getlist("qty[]")
    units = form.getlist("unit[]")
    prices = form.getlist("unit_price[]")
    currencies = form.getlist("currency[]")

    items = []
    for i in range(len(reqs)):
        if not reqs[i].strip():
            continue
        # Safely access parallel lists — some form fields may be missing/shorter.
        sr_val = sr_nos[i] if i < len(sr_nos) else ""
        items.append(QuotationItem(
            sr_no=int(sr_val) if sr_val else i + 1,
            customer_requirement=reqs[i].strip(),
            sql_code=codes[i].strip() if i < len(codes) else "",
            qty=float(qtys[i]) if i < len(qtys) and qtys[i] else 1,
            unit=units[i].strip() if i < len(units) and units[i] else "Nos.",
            unit_price=float(prices[i]) if i < len(prices) and prices[i] else 0,
            currency=currencies[i].strip() if i < len(currencies) and currencies[i] else "INR",
        ))
    return items


@quotations_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_quotation():
    settings = db.session.get(CompanySettings, 1)

    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        if not customer_id:
            flash("Please select or create a customer first.", "danger")
            return redirect(url_for("quotations.new_quotation"))

        q = Quotation(
            quotation_no=next_quotation_no(settings.quotation_prefix, current_user.initials, date.today()),
            date=date.today(),
            customer_id=customer_id,
            kind_attention=request.form.get("kind_attention", "").strip(),
            email=request.form.get("email", "").strip(),
            customer_gst_no=request.form.get("customer_gst_no", "").strip(),
            inquiry_ref=request.form.get("inquiry_ref", "").strip(),
            hsn_code=request.form.get("hsn_code", "").strip(),
            items_list_title=request.form.get("items_list_title", "Recommended Spare Part List").strip(),
            salesperson_id=current_user.id,
            freight_charges=float(request.form.get("freight_charges") or 0),
            tax_type=request.form.get("tax_type", "CGST_SGST"),
            tax_percent=float(request.form.get("tax_percent") or 18),
            scope=request.form.get("scope", "").strip(),
            taxes_note=request.form.get("taxes_note", "").strip(),
            payment_terms=request.form.get("payment_terms", "").strip(),
            delivery_period=request.form.get("delivery_period", "").strip(),
            packing_charges=request.form.get("packing_charges", "").strip(),
            warranty_terms=request.form.get("warranty_terms", "").strip(),
            price_validity=request.form.get("price_validity", "").strip(),
            status="Draft",
        )
        q.items = _parse_items_from_form(request.form)
        db.session.add(q)
        db.session.commit()
        flash(f"Quotation {q.quotation_no} created.", "success")
        return redirect(url_for("quotations.view_quotation", quotation_id=q.id))

    customers = Customer.query.order_by(Customer.name).all()
    return render_template("quotation_form.html", customers=customers, settings=settings,
                            quotation=None, today=date.today().isoformat(),
                            existing_items_json="[]")


@quotations_bp.route("/<int:quotation_id>/edit", methods=["GET", "POST"])
@login_required
def edit_quotation(quotation_id):
    q = Quotation.query.get_or_404(quotation_id)
    settings = db.session.get(CompanySettings, 1)

    if request.method == "POST":
        q.customer_id = request.form.get("customer_id")
        q.kind_attention = request.form.get("kind_attention", "").strip()
        q.email = request.form.get("email", "").strip()
        q.customer_gst_no = request.form.get("customer_gst_no", "").strip()
        q.inquiry_ref = request.form.get("inquiry_ref", "").strip()
        q.hsn_code = request.form.get("hsn_code", "").strip()
        q.items_list_title = request.form.get("items_list_title", "Recommended Spare Part List").strip()
        q.freight_charges = float(request.form.get("freight_charges") or 0)
        q.tax_type = request.form.get("tax_type", "CGST_SGST")
        q.tax_percent = float(request.form.get("tax_percent") or 18)
        q.scope = request.form.get("scope", "").strip()
        q.taxes_note = request.form.get("taxes_note", "").strip()
        q.payment_terms = request.form.get("payment_terms", "").strip()
        q.delivery_period = request.form.get("delivery_period", "").strip()
        q.packing_charges = request.form.get("packing_charges", "").strip()
        q.warranty_terms = request.form.get("warranty_terms", "").strip()
        q.price_validity = request.form.get("price_validity", "").strip()

        q.items = _parse_items_from_form(request.form)
        db.session.commit()
        flash(f"Quotation {q.quotation_no} updated.", "success")
        return redirect(url_for("quotations.view_quotation", quotation_id=q.id))

    customers = Customer.query.order_by(Customer.name).all()
    items_data = [
        {
            "sr_no": it.sr_no, "customer_requirement": it.customer_requirement,
            "sql_code": it.sql_code, "qty": it.qty, "unit": it.unit,
            "unit_price": it.unit_price, "currency": it.currency,
        }
        for it in q.items
    ]
    return render_template("quotation_form.html", customers=customers, settings=settings,
                            quotation=q, today=date.today().isoformat(),
                            existing_items_json=json.dumps(items_data))


@quotations_bp.route("/<int:quotation_id>")
@login_required
def view_quotation(quotation_id):
    q = Quotation.query.get_or_404(quotation_id)
    settings = db.session.get(CompanySettings, 1)
    return render_template("quotation_view.html", q=q, settings=settings)


@quotations_bp.route("/<int:quotation_id>/pdf")
@login_required
def quotation_pdf(quotation_id):
    q = Quotation.query.get_or_404(quotation_id)
    settings = db.session.get(CompanySettings, 1)
    buf = build_quotation_pdf(q, settings)
    filename = q.quotation_no.replace("/", "-") + ".pdf"
    return send_file(buf, as_attachment=True, download_name=filename, mimetype="application/pdf")


@quotations_bp.route("/<int:quotation_id>/status", methods=["POST"])
@login_required
def update_status(quotation_id):
    q = Quotation.query.get_or_404(quotation_id)
    new_status = request.form.get("status")
    if new_status in ("Draft", "Sent", "Confirmed", "Rejected"):
        q.status = new_status
        if new_status == "Confirmed":
            q.po_number = request.form.get("po_number", "").strip()
            po_date_str = request.form.get("po_date", "")
            q.po_date = datetime.strptime(po_date_str, "%Y-%m-%d").date() if po_date_str else date.today()
        db.session.commit()
        flash(f"Quotation {q.quotation_no} marked as {new_status}.", "success")
    return redirect(url_for("quotations.view_quotation", quotation_id=q.id))


@quotations_bp.route("/<int:quotation_id>/delete", methods=["POST"])
@login_required
def delete_quotation(quotation_id):
    q = Quotation.query.get_or_404(quotation_id)
    db.session.delete(q)
    db.session.commit()
    flash("Quotation deleted.", "success")
    return redirect(url_for("quotations.list_quotations"))
