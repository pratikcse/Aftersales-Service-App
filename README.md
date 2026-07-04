# Aftersales Portal (Flask)

A self-contained web app to replace the Excel-based quotation / confirmation / work-order
process. Runs entirely on Flask + SQLite — no external services required, so it can be
deployed on a local machine or your office intranet.

## What it does

- **Login** — individual accounts per salesperson (name/email + password).
- **Customer master** — save customers once, reuse them (with autofill) on every quotation.
- **Item master** — your ~2,900-row spare-parts price list is imported into the database.
  While typing a line item on a quotation, it's searchable by code or description with
  live autocomplete, and pulls in the unit, rate and item code automatically.
- **Quotations** — auto-numbered (`SP/HCR/26-27/PNR/JUL/1` style — configurable prefix,
  financial-year, your initials, month, running sequence), replicates the layout of your
  existing quotation format (including the yellow-highlighted Scope/Payment Terms rows,
  HSN code line, and an editable "Recommended Spare Part List for ___" subtitle),
  computes CGST+SGST / IGST / no-tax totals, and is downloadable as a PDF that matches
  your paper template.
- **Company logo** — upload it once under Settings; it appears top-left of the letterhead
  band, next to the company name/address, on every quotation and work order (screen and PDF).
- **Confirmation** — mark a quotation Draft → Sent → Confirmed (capturing the customer's PO
  number & date) or Rejected.
- **Work Orders** — generate a Work Order directly from a Confirmed quotation (copies the
  line items), track status Pending → In Progress → Dispatched → Completed, and download
  as PDF.
- **Company Settings** (admin only) — your real letterhead, GST/PAN/CIN, bank details, and
  default Terms & Conditions text live here — edit once, applied to every future PDF.

## 1. Install

Requires Python 3.10+.

```bash
cd aftersales_app
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Load your item master

Your CSV export of the master spare-parts sheet is already copied in as
`data/item_master.csv` (2,927 items imported and tested). To reload it any time your
Excel master sheet changes, export it as CSV again (same column headers) and run:

```bash
python import_items.py data/item_master.csv
```

Two price columns are read from the sheet: **Rate** (base/cost) and **PCR RATE**. When you
search for an item on a quotation, the app suggests the PCR rate if one exists (that's what
your sample quotation was priced from), otherwise it falls back to Rate. You can always
overwrite the price manually per line.

## 3. First run

```bash
python app.py
```

Open **http://localhost:5000** — since no user exists yet you'll land on a one-time setup
page to create the first Admin account. That account can then add the rest of the sales
team from **Users**, and should fill in your real company details under **Settings**
(the letterhead/GST/PAN/CIN/bank fields are placeholders until you do this — nothing
sensitive was hard-coded).

## 4. Deploying on your office network

For anything beyond your own testing, run it with a production WSGI server instead of the
Flask dev server, e.g.:

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=8080 app:create_app
```

Then anyone on the office LAN can reach it at `http://<this-pc's-IP>:8080`. To keep it
running in the background on Windows/Linux, use a tool like `nssm` (Windows service) or a
`systemd` unit (Linux) pointing at that same command.

**Change the secret key** before real use — set an environment variable so sessions aren't
tied to the default dev key:

```bash
export SECRET_KEY="something-long-and-random"     # Windows: set SECRET_KEY=...
```

## 5. Backups

Everything lives in one file: `aftersales.db` (SQLite). Back it up regularly (copy the
file) — that's your entire quotations/work-orders/customers/settings database.

## Project layout

```
app.py                 – Flask app factory, run this to start the server
models.py               – database tables (User, Customer, Item, Quotation, WorkOrder, ...)
numbering.py             – quotation/work-order auto-numbering logic
import_items.py          – loads data/item_master.csv into the Item table
blueprints/
  auth.py                – login/logout/user management
  main.py                 – dashboard, customers, item search API, company settings
  quotations.py            – quotation create/edit/view/PDF/status
  workorders.py             – work order create/view/PDF/status
utils/pdf_generator.py     – builds the quotation & work order PDFs (reportlab)
templates/                 – all HTML pages
static/                    – CSS + the quotation-form JavaScript (line items, autocomplete, live totals)
data/item_master.csv        – your spare parts master list
```

## Upgrading from an earlier copy of this app

If you already have an `aftersales.db` from a previous version, just drop in these updated
files and restart — the app automatically adds any new columns it needs (logo, HSN code,
etc.) on startup without touching your existing quotations, customers, or users.

## Notes / next steps you may want

- Currently anyone logged in can edit/confirm any quotation. If you want salespeople to
  only see their own quotations, that's a small filter to add in `blueprints/quotations.py`.
- There's no automated email-sending yet (marking a quotation "Sent" is just a status flag) —
  wiring up SMTP so "Sent" actually emails the customer their PDF is a natural next step.
- Passwords for new users created via the Users page default to a temporary password
  (shown at creation) — there's no "forgot password" flow yet since this is intranet-only;
  an admin can just re-create the account if needed.
