from sqlalchemy import text
from extensions import db

# (table, column, sqlite column definition)
_NEW_COLUMNS = [
    ("company_settings", "logo_filename", "VARCHAR(255) DEFAULT ''"),
    ("quotation", "hsn_code", "VARCHAR(60) DEFAULT ''"),
    ("quotation", "items_list_title", "VARCHAR(200) DEFAULT 'Recommended Spare Part List'"),
]


def run_migrations():
    """Add any columns that don't exist yet. Safe to call on every startup."""
    with db.engine.connect() as conn:
        for table, column, coldef in _NEW_COLUMNS:
            existing = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
            existing_cols = {row[1] for row in existing}
            if existing_cols and column not in existing_cols:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {coldef}"))
                conn.commit()
