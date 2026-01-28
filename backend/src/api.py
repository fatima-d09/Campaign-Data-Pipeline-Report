import os
from decimal import Decimal
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from db import SessionLocal
from models import Committee, CommitteeTotals

load_dotenv()

app = FastAPI(title="Campaign Data Pipeline API", version="0.1.0")

# ✅ CORS (lets your frontend call this API)
# For now, allow all origins. Later in deploy you can restrict this.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def db_session() -> Session:
    return SessionLocal()


def to_float(v: Any) -> float | None:
    if v is None:
        return None
    if isinstance(v, Decimal):
        return float(v)
    try:
        return float(v)
    except Exception:
        return None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/committees/top")
def top_committees(
    cycle: int = Query(2024, description="Election cycle year"),
    limit: int = Query(25, ge=1, le=200),
):
    """
    Returns top committees by receipts for a cycle.
    """
    db = db_session()
    try:
        stmt = (
            select(Committee, CommitteeTotals)
            .join(CommitteeTotals, CommitteeTotals.committee_id == Committee.committee_id)
            .where(CommitteeTotals.cycle == cycle)
            .order_by(desc(CommitteeTotals.receipts))
            .limit(limit)
        )
        rows = db.execute(stmt).all()

        results = []
        for c, t in rows:
            results.append({
                "committee_id": c.committee_id,
                "name": c.name,
                "party": c.party,
                "committee_type": c.committee_type,
                "state": c.state,
                "cycle": t.cycle,
                "receipts": to_float(t.receipts),
                "disbursements": to_float(t.disbursements),
                "cash_on_hand_end": to_float(t.cash_on_hand_end),
                "debts_owed_by_committee": to_float(t.debts_owed_by_committee),
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            })

        return {"cycle": cycle, "count": len(results), "results": results}
    finally:
        db.close()


@app.get("/committees/search")
def search_committees(
    q: str = Query(..., min_length=2, description="Search term (committee name)"),
    limit: int = Query(25, ge=1, le=100),
):
    """
    Search committees by name (case-insensitive).
    """
    db = db_session()
    try:
        stmt = (
            select(Committee)
            .where(Committee.name.ilike(f"%{q}%"))
            .order_by(Committee.name.asc())
            .limit(limit)
        )
        rows = db.execute(stmt).scalars().all()

        results = []
        for c in rows:
            results.append({
                "committee_id": c.committee_id,
                "name": c.name,
                "party": c.party,
                "committee_type": c.committee_type,
                "state": c.state,
            })
        return {"q": q, "count": len(results), "results": results}
    finally:
        db.close()


@app.get("/committees/{committee_id}")
def committee_detail(
    committee_id: str,
    cycle: int = Query(2024, description="Cycle year to return totals for"),
):
    """
    Committee metadata + totals for a given cycle.
    """
    db = db_session()
    try:
        committee = db.get(Committee, committee_id)
        if not committee:
            return {"error": "committee not found", "committee_id": committee_id}

        stmt = (
            select(CommitteeTotals)
            .where(CommitteeTotals.committee_id == committee_id)
            .where(CommitteeTotals.cycle == cycle)
        )
        totals = db.execute(stmt).scalar_one_or_none()

        return {
            "committee": {
                "committee_id": committee.committee_id,
                "name": committee.name,
                "party": committee.party,
                "committee_type": committee.committee_type,
                "state": committee.state,
                "updated_at": committee.updated_at.isoformat() if committee.updated_at else None,
            },
            "totals": None if not totals else {
                "cycle": totals.cycle,
                "receipts": to_float(totals.receipts),
                "disbursements": to_float(totals.disbursements),
                "cash_on_hand_end": to_float(totals.cash_on_hand_end),
                "debts_owed_by_committee": to_float(totals.debts_owed_by_committee),
                "updated_at": totals.updated_at.isoformat() if totals.updated_at else None,
            }
        }
    finally:
        db.close()
