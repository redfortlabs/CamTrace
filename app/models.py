import os
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, sessionmaker

Base = declarative_base()


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    camera_id: Mapped[str] = mapped_column(String, index=True)
    dst_ip: Mapped[str] = mapped_column(String, index=True)
    dst_port: Mapped[int] = mapped_column(Integer)
    protocol: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)

    # enrichment
    rdns: Mapped[str | None] = mapped_column(String, nullable=True)
    asn: Mapped[int | None] = mapped_column(Integer, nullable=True)
    as_org: Mapped[str | None] = mapped_column(String, nullable=True)
    country: Mapped[str | None] = mapped_column(String, nullable=True)
    region: Mapped[str | None] = mapped_column(String, nullable=True)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    violation: Mapped[int] = mapped_column(Integer, default=0)  # 0/1


def get_engine(db_path: str = "data/camtrace.sqlite"):
    """
    Ensure the SQLite parent directory exists in CI and local runs, then
    return a SQLAlchemy engine with safe SQLite threading config.
    """
    parent = os.path.dirname(db_path) or "."
    os.makedirs(parent, exist_ok=True)

    # check_same_thread=False: allow usage across FastAPI worker threads.
    return create_engine(
        f"sqlite:///{db_path}",
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
    )


def get_sessionmaker(engine):
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)
