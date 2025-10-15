from __future__ import annotations
from datetime import date as GDate, datetime
from jdatetime import date as JDate 

def gregorian_to_jalali(d: GDate | datetime | str, *, as_string: bool = False, sep: str = "-") -> JDate | str:
    """
    Convert Gregorian date -> Jalali (Persian).
    Accepts: datetime.date, datetime.datetime, or ISO 'YYYY-MM-DD' string.
    Returns: jdatetime.date or 'YYYY-MM-DD' string (ASCII digits).
    """
    # normalize to datetime.date
    if isinstance(d, str):
        d = GDate.fromisoformat(d)
    elif isinstance(d, datetime):
        d = d.date()
    elif not isinstance(d, GDate):
        raise TypeError("d must be a date, datetime, or ISO 'YYYY-MM-DD' string")

    j = JDate.fromgregorian(date=d)
    if as_string:
        return f"{j.year:04d}{sep}{j.month:02d}{sep}{j.day:02d}"
    return j

def jalali_to_gregorian(d: JDate | str, *, as_string: bool = False, sep: str = "-") -> GDate | str:
    """
    Convert Jalali (Persian) date -> Gregorian.
    Accepts: jdatetime.date or 'YYYY-MM-DD' (or 'YYYY/MM/DD') string with ASCII digits.
    Returns: datetime.date or 'YYYY-MM-DD' string (ASCII digits).
    """
    if isinstance(d, str):
        parts = d.replace("/", "-").split("-")
        if len(parts) < 3:
            raise ValueError("Jalali string must be 'YYYY-MM-DD' or 'YYYY/MM/DD'")
        jy, jm, jd = map(int, parts[:3])
        j = JDate(jy, jm, jd)
    elif isinstance(d, JDate):
        j = d
    else:
        raise TypeError("d must be a jdatetime.date or 'YYYY-MM-DD'/'YYYY/MM/DD' string")

    g = j.togregorian()  # -> datetime.date
    if as_string:
        return f"{g.year:04d}{sep}{g.month:02d}{sep}{g.day:02d}"
    return g



months = [
        (140311, "۱۴۰۳ بهمن"),
        (140312, "اسفند ۱۴۰۳"),
        (140401,"فروردین ۱۴۰۴"),
        (140402,"۱۴۰۴ اردیبهشت"),
        (140403,"خرداد ۱۴۰۴"),
        (140404,"تیر ۱۴۰۴"),
        (140405,"مرداد ۱۴۰۴"),
        (140406,"شهریور ۱۴۰۴"),
        (140407,"مهر ۱۴۰۴"),
        (140408,"آبان ۱۴۰۴"),
        (140409,"آذر ۱۴۰۴"),
        (140410, "دی ۱۴۰۴"),
        (140411, "بهمن ۱۴۰۴"),
        (140412, "اسفند ۱۴۰۴"),
    ]

def show_amount(amount):
    return f'{round(amount / 100000000)*1000:,}'

reserve_names = ["صندوق", "رزرو", "reserve", "cash", "bank", "بانک"]

