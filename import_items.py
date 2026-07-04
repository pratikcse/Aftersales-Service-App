"""
Import (or re-import) the spare-parts master list from data/item_master.csv into the database.

Usage:
    python import_items.py                 # imports data/item_master.csv
    python import_items.py path/to/file.csv # imports a different file

Re-running this wipes and reloads the Item table, so it's safe to use whenever
the sales team hands over an updated master sheet exported from Excel as CSV.
Expected columns (header row, any order):
    Item Code, Item Description, Unit, Rate, PCR RATE, FINAL ITEM NUMBER,
    Technical description   rating & size & & Make & MPN & Type
"""
import csv
import sys

from app import create_app
from extensions import db
from models import Item


def clean_float(val):
    if val is None:
        return 0.0
    val = str(val).replace(",", "").strip()
    if val == "":
        return 0.0
    try:
        return float(val)
    except ValueError:
        return 0.0


def import_csv(path):
    app = create_app()
    with app.app_context():
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        Item.query.delete()
        count = 0
        for row in rows:
            desc = (row.get("Item Description") or "").strip()
            if not desc:
                continue  # skip blank spacer rows from the Excel export
            item = Item(
                item_code=(row.get("Item Code") or "").strip(),
                description=desc,
                unit=(row.get("Unit") or "Nos.").strip() or "Nos.",
                rate=clean_float(row.get("Rate")),
                pcr_rate=clean_float(row.get("PCR RATE")),
                final_item_number=(row.get("FINAL ITEM NUMBER") or "").strip(),
                technical_description=(row.get("Technical description   rating & size & & Make & MPN & Type") or "").strip(),
            )
            db.session.add(item)
            count += 1
        db.session.commit()
        print(f"Imported {count} items from {path}")


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "data/item_master.csv"
    import_csv(csv_path)
