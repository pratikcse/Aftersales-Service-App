from datetime import date, datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from flask_login import login_required, current_user

from extensions import db
from models import WorkOrder, Quotation, CompanySettings
from numbering import next_wo_no
from utils.pdf_generator import build_workorder_pdf

workorders_bp = Blueprint("workorders", __name__, url_prefix="/workorders")


@workorders_bp.route("/")
@login_required
def list_workorders():
    status = request.args.get("status", "")
    query = WorkOrder.query
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(WorkOrder.created_at.desc()).all()
    return render_template("workorder_list.html", orders=orders, status=status)


@workorders_bp.route("/new/<int:quotation_id>", methods=["GET", "POST"])
@login_required
def new_workorder(quotation_id):
    q = Quotation.query.get_or_404(quotation_id)
    if q.status != "Confirmed":
        flash("Only a Confirmed quotation can be converted into a work order.", "danger")
        return redirect(url_for("quotations.view_quotation", quotation_id=q.id))

    if request.method == "POST":
        wo = WorkOrder(
            wo_no=next_wo_no(date.today()),
            date=date.today(),
            quotation_id=q.id,
            status="Pending",
            remarks=request.form.get("remarks", "").strip(),
            created_by_id=current_user.id,
        )
        delivery_str = request.form.get("expected_delivery_date", "")
        if delivery_str:
            wo.expected_delivery_date = datetime.strptime(delivery_str, "%Y-%m-%d").date()
        db.session.add(wo)
        db.session.commit()
        flash(f"Work Order {wo.wo_no} created.", "success")
        return redirect(url_for("workorders.view_workorder", wo_id=wo.id))

    return render_template("workorder_form.html", q=q)


@workorders_bp.route("/<int:wo_id>")
@login_required
def view_workorder(wo_id):
    wo = WorkOrder.query.get_or_404(wo_id)
    settings = db.session.get(CompanySettings, 1)
    return render_template("workorder_view.html", wo=wo, settings=settings)


@workorders_bp.route("/<int:wo_id>/pdf")
@login_required
def workorder_pdf(wo_id):
    wo = WorkOrder.query.get_or_404(wo_id)
    settings = db.session.get(CompanySettings, 1)
    buf = build_workorder_pdf(wo, settings)
    filename = wo.wo_no.replace("/", "-") + ".pdf"
    return send_file(buf, as_attachment=True, download_name=filename, mimetype="application/pdf")


@workorders_bp.route("/<int:wo_id>/status", methods=["POST"])
@login_required
def update_status(wo_id):
    wo = WorkOrder.query.get_or_404(wo_id)
    new_status = request.form.get("status")
    if new_status in ("Pending", "In Progress", "Dispatched", "Completed"):
        wo.status = new_status
        db.session.commit()
        flash(f"Work Order {wo.wo_no} marked as {new_status}.", "success")
    return redirect(url_for("workorders.view_workorder", wo_id=wo.id))
