from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base


class Committee(Base):
    __tablename__ = "committees"

    committee_id: Mapped[str] = mapped_column(String(9), primary_key=True)  # e.g. C007...
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    party: Mapped[str | None] = mapped_column(String(10), nullable=True)
    committee_type: Mapped[str | None] = mapped_column(String(10), nullable=True)
    state: Mapped[str | None] = mapped_column(String(2), nullable=True)

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    totals = relationship("CommitteeTotals", back_populates="committee", cascade="all, delete-orphan")


class CommitteeTotals(Base):
    __tablename__ = "committee_totals"
    __table_args__ = (
        UniqueConstraint("committee_id", "cycle", name="uq_committee_cycle"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    committee_id: Mapped[str] = mapped_column(ForeignKey("committees.committee_id"), nullable=False)
    cycle: Mapped[int] = mapped_column(Integer, nullable=False)

    receipts: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    disbursements: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    cash_on_hand_end: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    debts_owed_by_committee: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)

    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    committee = relationship("Committee", back_populates="totals")
