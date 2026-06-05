"""DML on Cloud Spanner with SQLAlchemy (sqlalchemy-spanner dialect).

You define Python classes mapped to tables, then add / change / delete objects
through a Session. SQLAlchemy emits the SQL for you. This is the most portable
option — the same code targets PostgreSQL, MySQL, etc. by swapping the URL.

Connection URL format:
    spanner+spanner:///projects/<PROJECT>/instances/<INSTANCE>/databases/<DB>

Spanner note: it has no auto-increment, so primary keys are assigned by you.
"""

from sqlalchemy import create_engine, Boolean, Integer, String, select
from sqlalchemy.orm import declarative_base, Session, Mapped, mapped_column

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PROJECT_ID, INSTANCE_ID, DATABASE_ID

Base = declarative_base()


class Singer(Base):
    __tablename__ = "Singers"

    SingerId: Mapped[int] = mapped_column(Integer, primary_key=True)
    FirstName: Mapped[str] = mapped_column(String(1024))
    LastName: Mapped[str] = mapped_column(String(1024))
    Active: Mapped[bool] = mapped_column(Boolean)


def main():
    url = (
        f"spanner+spanner:///projects/{PROJECT_ID}"
        f"/instances/{INSTANCE_ID}/databases/{DATABASE_ID}"
    )
    engine = create_engine(url)

    with Session(engine) as session:
        # ---- INSERT --------------------------------------------------------
        session.add_all(
            [
                Singer(SingerId=1, FirstName="Marc", LastName="Richards", Active=True),
                Singer(SingerId=2, FirstName="Catalina", LastName="Smith", Active=True),
                Singer(SingerId=3, FirstName="Alice", LastName="Trentor", Active=False),
            ]
        )
        session.commit()

        # ---- UPDATE (load, mutate object, commit) -------------------------
        singer = session.get(Singer, 3)
        singer.Active = True
        session.commit()

        # ---- DELETE --------------------------------------------------------
        session.delete(session.get(Singer, 2))
        session.commit()

        print("SQLAlchemy DML committed.")

        # ---- Read back to verify ------------------------------------------
        for singer in session.scalars(select(Singer).order_by(Singer.SingerId)):
            print(singer.SingerId, singer.FirstName, singer.Active)


if __name__ == "__main__":
    main()
