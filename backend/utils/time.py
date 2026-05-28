from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo


TZ_SP = ZoneInfo("America/Sao_Paulo")


def now_sp_naive() -> datetime:
    """Return Sao Paulo time without tzinfo for DB comparisons/inserts."""
    return datetime.now(TZ_SP).replace(tzinfo=None)


def week_bounds_sp(ref: datetime | None = None) -> tuple[date, date]:
    """Return (monday, sunday) for the week in Sao Paulo timezone."""
    base = ref or now_sp_naive()
    weekday = base.weekday()  # Monday=0
    monday = (base - timedelta(days=weekday)).date()
    sunday = monday + timedelta(days=6)
    return monday, sunday


def combine_date_time(day: date, time_value: time) -> datetime:
    return datetime.combine(day, time_value)


def hours_to_time(hour: int) -> time:
    return time(hour=hour, minute=0)


def add_hours(dt: datetime, hours: int) -> datetime:
    return dt + timedelta(hours=hours)


def hours_until(start: datetime, ref: datetime | None = None) -> float:
    base = ref or now_sp_naive()
    delta = start - base
    return delta.total_seconds() / 3600.0
