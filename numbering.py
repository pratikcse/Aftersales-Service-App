from datetime import date
from extensions import db
from models import Counter


def financial_year(d: date) -> str:
    """India FY runs Apr->Mar. Returns e.g. '26-27' for any date between Apr-2026 and Mar-2027."""
    if d.month >= 4:
        start, end = d.year, d.year + 1
    else:
        start, end = d.year - 1, d.year
    return f"{str(start)[-2:]}-{str(end)[-2:]}"


def next_sequence(key: str) -> int:
    counter = db.session.get(Counter, key)
    if counter is None:
        counter = Counter(key=key, value=0)
        db.session.add(counter)
    counter.value += 1
    db.session.commit()
    return counter.value


def next_quotation_no(prefix: str, salesperson_initials: str, d: date) -> str:
    fy = financial_year(d)
    seq = next_sequence(f"quotation-{fy}")
    month = d.strftime("%b").upper()
    return f"{prefix}/{fy}/{salesperson_initials}/{month}/{seq}"


def next_wo_no(d: date) -> str:
    fy = financial_year(d)
    seq = next_sequence(f"workorder-{fy}")
    return f"WO/{fy}/{seq:04d}"
