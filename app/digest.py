"""The morning digest: yesterday in six lines (on Sunday, Thursday to Saturday).

Runs as a Railway cron service (`python -m app.digest`, schedule in README.md)
or through POST /internal/digest. It only reads; the rows it reports were
written by the chat turns during the day.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from .config import settings
from .db import Invoice, Message, Run, SessionLocal, init_db


# date.weekday(): Monday is 0.
_HEBREW_DAYS = ["יום שני", "יום שלישי", "יום רביעי", "יום חמישי", "יום שישי", "שבת", "יום ראשון"]


def _local_bounds(day: date) -> tuple[datetime, datetime]:
    tz = ZoneInfo(settings.timezone)
    start = datetime.combine(day, time.min, tzinfo=tz).astimezone(timezone.utc).replace(tzinfo=None)
    end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=tz).astimezone(timezone.utc).replace(tzinfo=None)
    return start, end


def _covered_days(today: date) -> tuple[date, date]:
    """Sunday covers Thursday to Saturday (no digest runs on Friday or Saturday); other days cover yesterday."""
    last = today - timedelta(days=1)
    first = today - timedelta(days=3) if today.weekday() == 6 else last
    return first, last


def build_digest(db: Session, today: date | None = None) -> str:
    tz = ZoneInfo(settings.timezone)
    today = today or datetime.now(tz).date()
    first, last = _covered_days(today)
    start, end = _local_bounds(first)[0], _local_bounds(last)[1]
    if first == last:
        title = f"סיכום בוקר על אתמול — {_HEBREW_DAYS[last.weekday()]} {last.strftime('%d.%m.%Y')}"
    else:
        title = f"סיכום בוקר על חמישי עד שבת — {first.strftime('%d.%m')}–{last.strftime('%d.%m.%Y')}"

    invoices = db.scalars(select(Invoice).where(Invoice.created_at >= start, Invoice.created_at < end)
                          .order_by(Invoice.created_at)).all()
    logged = [i for i in invoices if i.status == "logged"]
    needs = [i for i in invoices if i.status == "needs_a_look"]
    flagged = [i for i in invoices if i.flagged]
    total = sum(i.amount or 0 for i in logged)

    messages = db.scalar(select(func.count()).select_from(Message)
                         .where(Message.role == "user", Message.created_at >= start, Message.created_at < end)) or 0
    runs = db.execute(select(func.count(Run.id), func.coalesce(func.sum(Run.cost_usd), 0.0),
                             func.sum(case((Run.status != "ok", 1), else_=0)))
                      .where(Run.created_at >= start, Run.created_at < end)).one()
    run_count, cost, not_ok = int(runs[0] or 0), float(runs[1] or 0.0), int(runs[2] or 0)

    lines = [f"{title} · Lavender Bakery Copilot",
             f"חשבוניות שנרשמו: {len(logged)} · סה\"כ ₪{total:,.0f}",
             f"דורשות בדיקה: {len(needs)}" + (" — " + "; ".join(f"{i.supplier} ({i.invoice_number or 'ללא מספר'})" for i in needs[:5]) if needs else ""),
             f"מסומנות מעל ₪5,000: {len(flagged)}" + (" — " + "; ".join(f"{i.supplier} ₪{i.amount:,.0f}" for i in flagged[:5]) if flagged else ""),
             f"צ'אט: {messages} הודעות · {run_count} פניות למודל · ${cost:.2f} (התקרה: ${settings.daily_cap_usd:.2f} ליום)",
             f"פניות שנכשלו: {not_ok}" + (" — לבדוק את טבלת runs ואת runbook.md" if not_ok else "")]
    return "\n".join(lines)


def send_digest(text: str) -> bool:
    """POST {"text": ...} to DIGEST_WEBHOOK_URL (Slack-compatible). Returns False when no URL is set."""
    if not settings.digest_webhook_url:
        return False
    import httpx

    r = httpx.post(settings.digest_webhook_url, json={"text": text}, timeout=15)
    r.raise_for_status()
    return True


def main() -> None:
    init_db()
    with SessionLocal() as db:
        body = build_digest(db)
    print(body)
    sent = send_digest(body)
    print(f"\n[sent to webhook: {sent}]")


if __name__ == "__main__":
    main()
