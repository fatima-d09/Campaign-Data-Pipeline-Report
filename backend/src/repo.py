from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from models import Committee, CommitteeTotals


def upsert_committee(db: Session, committee_data: dict) -> None:
    """
    Upsert into committees table by committee_id.
    """
    stmt = insert(Committee).values(**committee_data)
    update_cols = {
        "name": stmt.excluded.name,
        "party": stmt.excluded.party,
        "committee_type": stmt.excluded.committee_type,
        "state": stmt.excluded.state,
    }
    stmt = stmt.on_conflict_do_update(
        index_elements=[Committee.committee_id],
        set_=update_cols,
    )
    db.execute(stmt)


def upsert_committee_totals(db: Session, totals_data: dict) -> None:
    """
    Upsert into committee_totals table by (committee_id, cycle).
    """
    stmt = insert(CommitteeTotals).values(**totals_data)
    update_cols = {
        "receipts": stmt.excluded.receipts,
        "disbursements": stmt.excluded.disbursements,
        "cash_on_hand_end": stmt.excluded.cash_on_hand_end,
        "debts_owed_by_committee": stmt.excluded.debts_owed_by_committee,
    }
    stmt = stmt.on_conflict_do_update(
        constraint="uq_committee_cycle",
        set_=update_cols,
    )
    db.execute(stmt)


def committee_exists(db: Session, committee_id: str) -> bool:
    return db.execute(
        select(Committee.committee_id).where(Committee.committee_id == committee_id)
    ).first() is not None
