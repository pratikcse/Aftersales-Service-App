from io import BytesIO
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

BAND_BLUE = colors.HexColor("#BFE3F0")
HEADER_YELLOW = colors.HexColor("#FFFF00")
LINE_GREY = colors.HexColor("#666666")

styles = getSampleStyleSheet()
P = styles["Normal"]
P.fontName = "Helvetica"
P.fontSize = 9
P.leading = 12

BOLD = ParagraphStyle("bold", parent=P, fontName="Helvetica-Bold")
TITLE = ParagraphStyle("title", parent=P, fontName="Helvetica-Bold", fontSize=16, alignment=TA_CENTER)
SMALL = ParagraphStyle("small", parent=P, fontSize=8, leading=10)
LABEL = ParagraphStyle("label", parent=P, fontName="Helvetica-Oblique", fontSize=9)


def _p(text, style=P):
    return Paragraph(str(text) if text is not None else "", style)


def _logo_path(settings):
    if not settings.logo_filename:
        return None
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "static", "uploads", settings.logo_filename)
    return path if os.path.exists(path) else None


def _company_header_table(settings):
    text_cell = _p(f"<b>{settings.company_name}</b><br/>{settings.address_line.replace(chr(10), '<br/>')}", BOLD)
    logo_path = _logo_path(settings)

    if logo_path:
        try:
            logo_img = Image(logo_path, width=28 * mm, height=16 * mm, kind="proportional")
        except Exception:
            logo_img = ""
        data = [[logo_img, text_cell]]
        t = Table(data, colWidths=[32 * mm, 138 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BAND_BLUE),
            ("BOX", (0, 0), (-1, -1), 0.75, LINE_GREY),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (0, -1), 8),
            ("LEFTPADDING", (1, 0), (1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ]))
        return t

    data = [[text_cell]]
    t = Table(data, colWidths=[170 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BAND_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.75, LINE_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def _gst_line(settings):
    return Table([[_p(f"<b>GST.NO :</b> {settings.gst_no}", SMALL)]], colWidths=[170 * mm],
                 style=TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 2)]))


def build_quotation_pdf(q, settings):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=15 * mm, rightMargin=15 * mm,
                             topMargin=10 * mm, bottomMargin=12 * mm)
    story = []

    story.append(_company_header_table(settings))
    story.append(_gst_line(settings))
    story.append(Spacer(1, 6))
    story.append(_p("QUOTATION", TITLE))
    story.append(Spacer(1, 4))

    # Quotation No / Date row
    qno_date = Table(
        [[_p(f"<b>Quotation No.</b>  {q.quotation_no}", P), _p(f"<b>Date :</b> {q.date.strftime('%d/%b/%Y')}", P)]],
        colWidths=[120 * mm, 50 * mm])
    qno_date.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(qno_date)

    cust = q.customer
    cust_block = Table([
        [_p("<b>Customer Name &amp; Address</b>", P), _p(f"{cust.name}<br/>{cust.address.replace(chr(10), '<br/>')}", P)],
        [_p("<b>Kind Attention :</b>", P), _p(q.kind_attention or "", P)],
        [_p("<b>Email ID</b>", P), _p(q.email or "", P)],
        [_p("<b>GST.NO.</b>", P), _p(q.customer_gst_no or "", P)],
        [_p("Your inquiry (a) Verbal, (b) mail, (c) tender, dated", SMALL), _p(q.inquiry_ref or "", P)],
    ], colWidths=[55 * mm, 115 * mm])
    cust_block.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(cust_block)
    story.append(Spacer(1, 8))

    story.append(_p("<b>Sub:</b> Offer for Spares with brief description.", P))
    story.append(Spacer(1, 4))
    story.append(_p("Dear Madam/Sir,", P))
    story.append(Spacer(1, 4))
    story.append(_p("<i><b>We thank you for your ref inquiry for subject equipment.</b> We are pleased to submit our most competitive offer as below</i>", P))
    story.append(Spacer(1, 6))
    story.append(_p("Annexure/s &amp; Attachment/s: -", P))
    story.append(_p("1. Price sheet.", P))
    story.append(_p("2. Standard Terms &amp; Conditions", P))
    story.append(_p("3. Bank Details", P))
    story.append(Spacer(1, 6))
    story.append(_p("<i>We hope our offer is in line with your requirement and shall be pleased to receive your valuable feedback</i>", P))
    story.append(_p("<i>Thanking You and Assuring our best services at all times</i>", P))
    story.append(Spacer(1, 8))

    story.append(_p("Yours Sincerely", P))
    sp = q.salesperson
    story.append(_p(f"<b>Name:</b> {sp.name}", P))
    story.append(_p(f"<b>Designation:</b> {sp.designation}", P))
    story.append(_p(f"<b>Handphone:</b> {sp.handphone}", P))
    story.append(_p(f"<b>E-mail :</b> {sp.email}", P))
    story.append(Spacer(1, 10))

    story.append(_p("<b>Annexure- I</b>", BOLD))
    story.append(_p(f"<b>{q.items_list_title or 'Recommended Spare Part List'}</b>", BOLD))
    story.append(Spacer(1, 4))

    # Line items table
    header = ["SR NO", "Customer Requirement", "SQL Code", "Qty.", "Unit", "Unit Price", "Currency", "Total Price"]
    rows = [header]
    for it in q.items:
        rows.append([
            str(it.sr_no), _p(it.customer_requirement, SMALL), it.sql_code or "",
            f"{it.qty:g}", it.unit, f"{it.unit_price:,.2f}", it.currency, f"{it.total_price:,.2f}",
        ])
    items_table = Table(rows, colWidths=[12 * mm, 62 * mm, 18 * mm, 12 * mm, 14 * mm, 22 * mm, 16 * mm, 24 * mm], repeatRows=1)
    items_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (3, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(items_table)

    if q.hsn_code:
        story.append(Spacer(1, 4))
        story.append(_p(f"<b>HSN CODE :</b> {q.hsn_code}", SMALL))

    # Totals block
    totals_rows = [["", "TOTAL", f"{q.subtotal:,.2f}"]]
    totals_rows.append(["", "Fright Charges", f"{q.freight_charges:,.2f}"])
    totals_rows.append(["", "TOTAL AMOUNT", f"{q.total_before_tax:,.2f}"])
    if q.tax_type == "CGST_SGST":
        totals_rows.append(["", f"CGST {q.tax_percent/2:g}%", f"{q.cgst_amount:,.2f}"])
        totals_rows.append(["", f"SGST {q.tax_percent/2:g}%", f"{q.sgst_amount:,.2f}"])
    elif q.tax_type == "IGST":
        totals_rows.append(["", f"IGST {q.tax_percent:g}%", f"{q.igst_amount:,.2f}"])
    totals_rows.append(["", "GRAND TOTAL", f"{q.grand_total:,.2f}"])
    totals_rows.append(["", "FINAL AMOUNT", f"{q.grand_total:,.2f}"])

    totals_table = Table(totals_rows, colWidths=[140 * mm, 30 * mm, 30 * mm])
    totals_table.setStyle(TableStyle([
        ("BOX", (1, 0), (-1, -1), 0.5, LINE_GREY),
        ("INNERGRID", (1, 0), (-1, -1), 0.5, LINE_GREY),
        ("FONTNAME", (1, -2), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (2, 0), (2, -1), 6),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 10))

    # Terms & Conditions
    story.append(_p("<b>Terms &amp; Condition</b>", BOLD))
    terms_rows = [["Sr.No.", "Commercial Terms"]]
    terms = [
        ("1", "Scope :-", q.scope),
        ("2", "Taxes,Duties, etc. :-", q.taxes_note),
        ("3", "Payment Terms :-", q.payment_terms),
        ("4", "Delivery Period :-", q.delivery_period),
        ("5", "Packing Charges :-", q.packing_charges),
        ("6", "Warranty Terms :-", q.warranty_terms),
        ("7", "Price Validity:-", q.price_validity),
    ]
    for num, label, val in terms:
        terms_rows.append([num, _p(f"<b>{label}</b> {val}", SMALL)])
    terms_table = Table(terms_rows, colWidths=[15 * mm, 155 * mm])
    terms_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("BACKGROUND", (0, 1), (-1, 1), HEADER_YELLOW),   # Scope
        ("BACKGROUND", (0, 3), (-1, 3), HEADER_YELLOW),   # Payment Terms
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(terms_table)
    story.append(Spacer(1, 8))

    # Bank details
    story.append(_p("<b>Bank Details</b>", BOLD))
    bank_rows = [[_p(
        f"Bank Name: {settings.bank_name} &nbsp;&nbsp; A/c No.: {settings.bank_account_no} "
        f"&nbsp;&nbsp; IFSC: {settings.bank_ifsc} &nbsp;&nbsp; Branch: {settings.bank_branch}", SMALL)]]
    bank_table = Table(bank_rows, colWidths=[170 * mm])
    bank_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(bank_table)
    story.append(Spacer(1, 6))

    footer_rows = [[
        _p(f"Telephone: {settings.telephone}<br/><b>{settings.company_name}</b><br/>{settings.address_line}", SMALL),
        _p(f"CIN: {settings.cin_no}<br/>GST.NO.: {settings.gst_no}<br/>PAN NO.: {settings.pan_no}", SMALL),
    ]]
    footer_table = Table(footer_rows, colWidths=[85 * mm, 85 * mm])
    footer_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(footer_table)

    doc.build(story)
    buf.seek(0)
    return buf


def build_workorder_pdf(wo, settings):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=15 * mm, rightMargin=15 * mm,
                             topMargin=10 * mm, bottomMargin=12 * mm)
    story = []
    q = wo.quotation
    cust = q.customer

    story.append(_company_header_table(settings))
    story.append(_gst_line(settings))
    story.append(Spacer(1, 6))
    story.append(_p("WORK ORDER", TITLE))
    story.append(Spacer(1, 4))

    info = Table([
        [_p(f"<b>Work Order No.</b> {wo.wo_no}", P), _p(f"<b>Date :</b> {wo.date.strftime('%d/%b/%Y')}", P)],
        [_p(f"<b>Against Quotation No.</b> {q.quotation_no}", P),
         _p(f"<b>Customer PO No.</b> {q.po_number or '-'}", P)],
        [_p(f"<b>Customer:</b> {cust.name}", P), _p(f"<b>Status:</b> {wo.status}", P)],
        [_p(f"<b>Expected Delivery:</b> {wo.expected_delivery_date.strftime('%d/%b/%Y') if wo.expected_delivery_date else '-'}", P),
         _p("", P)],
    ], colWidths=[85 * mm, 85 * mm])
    info.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(info)
    story.append(Spacer(1, 8))

    header = ["SR NO", "Item Description", "SQL Code", "Qty.", "Unit"]
    rows = [header]
    for it in q.items:
        rows.append([str(it.sr_no), _p(it.customer_requirement, SMALL), it.sql_code or "", f"{it.qty:g}", it.unit])
    items_table = Table(rows, colWidths=[15 * mm, 100 * mm, 25 * mm, 15 * mm, 15 * mm], repeatRows=1)
    items_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE_GREY),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (3, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 8))

    if wo.remarks:
        story.append(_p("<b>Remarks:</b>", BOLD))
        story.append(_p(wo.remarks, P))
        story.append(Spacer(1, 6))

    story.append(_p(f"<b>Prepared by:</b> {wo.created_by.name}", P))
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_GREY))
    story.append(Spacer(1, 6))
    story.append(_p(f"<b>{settings.company_name}</b> &nbsp;·&nbsp; {settings.address_line} &nbsp;·&nbsp; Tel: {settings.telephone}", SMALL))

    doc.build(story)
    buf.seek(0)
    return buf
