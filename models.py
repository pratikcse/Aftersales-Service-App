from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    initials = db.Column(db.String(10), nullable=False)  # e.g. PNR -> used in quotation numbering
    designation = db.Column(db.String(120), default="")
    handphone = db.Column(db.String(40), default="")
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, default="")
    state = db.Column(db.String(80), default="")
    gst_no = db.Column(db.String(30), default="")
    kind_attention = db.Column(db.String(120), default="")
    email = db.Column(db.String(120), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return self.name


class Item(db.Model):
    """Master spare-parts catalogue, imported from the Excel/CSV master sheet."""
    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(60), index=True)
    description = db.Column(db.Text, nullable=False)
    unit = db.Column(db.String(20), default="Nos.")
    rate = db.Column(db.Float, default=0)
    pcr_rate = db.Column(db.Float, default=0)
    final_item_number = db.Column(db.String(60), default="")
    technical_description = db.Column(db.Text, default="")


class CompanySettings(db.Model):
    """Singleton table (row id=1) holding letterhead / bank details used on PDFs."""
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), default="Your Company Pvt. Ltd.")
    address_line = db.Column(db.Text, default="Plot No. __, MIDC, Pune - 411 0__, India")
    state = db.Column(db.String(80), default="Maharashtra")
    gst_no = db.Column(db.String(30), default="27XXXXXXXXXXXZX")
    pan_no = db.Column(db.String(20), default="XXXXX0000X")
    cin_no = db.Column(db.String(30), default="U00000MH0000PLC000000")
    telephone = db.Column(db.String(60), default="+91-20-0000000")
    bank_name = db.Column(db.String(120), default="Bank Name")
    bank_account_no = db.Column(db.String(60), default="000000000000")
    bank_ifsc = db.Column(db.String(20), default="ABCD0123456")
    bank_branch = db.Column(db.String(120), default="Branch, City")
    quotation_prefix = db.Column(db.String(20), default="SP/HCR")  # editable code shown in quote no.
    logo_filename = db.Column(db.String(255), default="")  # served from /static/uploads/
    default_scope = db.Column(db.Text, default="Our scope is limited to design, manufacture, routine in-house tests & delivery on EXW Pune, India")
    default_taxes = db.Column(db.Text, default="Extra as applicable to Buyers account. Currently GST applicable is 18% on basic price. Other taxes if applicable during invoicing shall be borne by buyer.")
    default_payment_terms = db.Column(db.Text, default="Advance Payment -100% Advance prior to dispatch")
    default_delivery_period = db.Column(db.String(120), default="8-9 Weeks")
    default_packing_charges = db.Column(db.String(120), default="3% Extra on Basic")
    default_warranty_terms = db.Column(db.String(120), default="06 Months from date of invoice")
    default_price_validity = db.Column(db.String(120), default="15 Days from Submission date")


class Counter(db.Model):
    """Sequence counters, keyed by e.g. 'quotation-2026-27' or 'workorder-2026-27'."""
    key = db.Column(db.String(60), primary_key=True)
    value = db.Column(db.Integer, default=0)


class Quotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quotation_no = db.Column(db.String(80), unique=True, nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)

    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    customer = db.relationship("Customer")

    kind_attention = db.Column(db.String(120), default="")
    email = db.Column(db.String(120), default="")
    customer_gst_no = db.Column(db.String(30), default="")
    inquiry_ref = db.Column(db.String(200), default="")
    hsn_code = db.Column(db.String(60), default="")
    items_list_title = db.Column(db.String(200), default="Recommended Spare Part List")

    salesperson_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    salesperson = db.relationship("User")

    freight_charges = db.Column(db.Float, default=0)
    tax_type = db.Column(db.String(20), default="CGST_SGST")  # CGST_SGST | IGST | NONE
    tax_percent = db.Column(db.Float, default=18.0)

    scope = db.Column(db.Text, default="")
    taxes_note = db.Column(db.Text, default="")
    payment_terms = db.Column(db.Text, default="")
    delivery_period = db.Column(db.String(120), default="")
    packing_charges = db.Column(db.String(120), default="")
    warranty_terms = db.Column(db.String(120), default="")
    price_validity = db.Column(db.String(120), default="")

    status = db.Column(db.String(20), default="Draft")  # Draft | Sent | Confirmed | Rejected
    po_number = db.Column(db.String(120), default="")
    po_date = db.Column(db.Date, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("QuotationItem", backref="quotation", cascade="all, delete-orphan", order_by="QuotationItem.sr_no")
    work_orders = db.relationship("WorkOrder", backref="quotation")

    # ---- computed totals ----
    @property
    def subtotal(self):
        return sum(i.total_price for i in self.items)

    @property
    def total_before_tax(self):
        return self.subtotal + (self.freight_charges or 0)

    @property
    def tax_amount(self):
        return round(self.total_before_tax * (self.tax_percent or 0) / 100, 2)

    @property
    def cgst_amount(self):
        return round(self.tax_amount / 2, 2) if self.tax_type == "CGST_SGST" else 0

    @property
    def sgst_amount(self):
        return self.cgst_amount if self.tax_type == "CGST_SGST" else 0

    @property
    def igst_amount(self):
        return round(self.tax_amount, 2) if self.tax_type == "IGST" else 0

    @property
    def grand_total(self):
        if self.tax_type == "NONE":
            return round(self.total_before_tax, 2)
        return round(self.total_before_tax + self.tax_amount, 2)


class QuotationItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quotation_id = db.Column(db.Integer, db.ForeignKey("quotation.id"), nullable=False)
    sr_no = db.Column(db.Integer, default=1)
    customer_requirement = db.Column(db.Text, nullable=False)
    sql_code = db.Column(db.String(60), default="")  # SQL/SL Code shown on the quotation (from Item master)
    qty = db.Column(db.Float, default=1)
    unit = db.Column(db.String(20), default="Nos.")
    unit_price = db.Column(db.Float, default=0)
    currency = db.Column(db.String(10), default="INR")

    @property
    def total_price(self):
        return round((self.qty or 0) * (self.unit_price or 0), 2)


class WorkOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wo_no = db.Column(db.String(80), unique=True, nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    quotation_id = db.Column(db.Integer, db.ForeignKey("quotation.id"), nullable=False)

    expected_delivery_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), default="Pending")  # Pending | In Progress | Dispatched | Completed
    remarks = db.Column(db.Text, default="")

    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_by = db.relationship("User")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
