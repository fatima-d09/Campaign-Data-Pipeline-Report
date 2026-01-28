import argparse
import time

from db import SessionLocal
from fec_client import fec_get
from repo import upsert_committee, upsert_committee_totals
from utils import clean_str, to_decimal


def fetch_top_committees_by_receipts(cycle: int, per_page: int) -> list[dict]:
    """
    Uses /committees/totals/ endpoint.
    Returns committee totals rows (each includes committee_id and financial totals).
    """
    data = fec_get("/committees/totals/", {
        "cycle": cycle,
        "per_page": per_page,
        "sort": "-receipts",
        "page": 1,
    })
    return data.get("results", [])


def fetch_committee_metadata(committee_id: str) -> dict | None:
    data = fec_get(f"/committee/{committee_id}/", {"per_page": 1})
    results = data.get("results", [])
    return results[0] if results else None


def main():
    parser = argparse.ArgumentParser(description="Ingest top committees by receipts")
    parser.add_argument("--cycle", type=int, default=2024, help="Election cycle year")
    parser.add_argument("--top", type=int, default=25, help="How many committees to ingest")
    parser.add_argument("--sleep", type=float, default=0.15, help="Sleep between API calls (rate-limit friendly)")
    args = parser.parse_args()

    top_rows = fetch_top_committees_by_receipts(args.cycle, args.top)
    print(f"Fetched {len(top_rows)} committee totals rows for cycle {args.cycle}")

    db = SessionLocal()
    try:
        inserted = 0

        for row in top_rows:
            committee_id = clean_str(row.get("committee_id"))
            if not committee_id:
                continue

            # Fetch committee metadata (name, party, state, type)
            meta = fetch_committee_metadata(committee_id)
            if not meta:
                print(f"⚠️ No metadata found for {committee_id}")
                continue

            committee_payload = {
                "committee_id": committee_id,
                "name": clean_str(meta.get("name")) or "Unknown",
                "party": clean_str(meta.get("party")),
                "committee_type": clean_str(meta.get("committee_type")),
                "state": clean_str(meta.get("state")),
            }

            totals_payload = {
                "committee_id": committee_id,
                "cycle": args.cycle,
                "receipts": to_decimal(row.get("receipts")),
                "disbursements": to_decimal(row.get("disbursements")),
                "cash_on_hand_end": to_decimal(row.get("cash_on_hand_end")),
                "debts_owed_by_committee": to_decimal(row.get("debts_owed_by_committee")),
            }

            upsert_committee(db, committee_payload)
            upsert_committee_totals(db, totals_payload)

            inserted += 1
            if inserted % 5 == 0:
                db.commit()
                print(f"✅ Upserted {inserted}/{len(top_rows)}")

            time.sleep(args.sleep)

        db.commit()
        print(f"🎉 Done. Upserted {inserted} committees + totals.")

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
