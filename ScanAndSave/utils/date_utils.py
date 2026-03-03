from datetime import datetime


def parse_date(date_string: str):
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m/%d/%y",
        "%Y/%m/%d",
        "%B %d, %Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    return datetime.today()


def to_iso_string(dt: datetime):
    return dt.strftime("%Y-%m-%d")