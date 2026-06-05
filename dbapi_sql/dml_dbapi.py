"""DML on Cloud Spanner with raw SQL via the Python DB-API (PEP 249).

Plain "just run SQL" in pure Python. The DB-API driver ships *inside* the
google-cloud-spanner package, so no extra dependency is needed.

Key points
----------
* You write SQL strings and run them through a standard cursor.
* Parameters use %(name)s placeholders bound from a dict — never f-string your
  values into the SQL (that is how SQL injection happens).
* DML runs inside an implicit transaction; nothing persists until commit().
* Spanner does not support DB-generated keys, so you supply primary keys.
"""

from google.cloud.spanner_dbapi import connect

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PROJECT_ID, INSTANCE_ID, DATABASE_ID


def main():
    connection = connect(INSTANCE_ID, DATABASE_ID, project=PROJECT_ID)
    cursor = connection.cursor()

    try:
        # ---- INSERT --------------------------------------------------------
        cursor.execute(
            "INSERT INTO Singers (SingerId, FirstName, LastName, Active) "
            "VALUES (%(id)s, %(first)s, %(last)s, %(active)s)",
            {"id": 1, "first": "Marc", "last": "Richards", "active": True},
        )

        # ---- INSERT many (one round trip via executemany) ------------------
        cursor.executemany(
            "INSERT INTO Singers (SingerId, FirstName, LastName, Active) "
            "VALUES (%(id)s, %(first)s, %(last)s, %(active)s)",
            [
                {"id": 2, "first": "Catalina", "last": "Smith", "active": True},
                {"id": 3, "first": "Alice", "last": "Trentor", "active": False},
            ],
        )

        # ---- UPDATE --------------------------------------------------------
        cursor.execute(
            "UPDATE Singers SET Active = %(active)s WHERE SingerId = %(id)s",
            {"active": True, "id": 3},
        )

        # ---- DELETE --------------------------------------------------------
        cursor.execute(
            "DELETE FROM Singers WHERE SingerId = %(id)s",
            {"id": 2},
        )

        # Persist all of the above atomically.
        connection.commit()
        print("DB-API DML committed.")

        # ---- Read back to verify ------------------------------------------
        cursor.execute("SELECT SingerId, FirstName, Active FROM Singers ORDER BY SingerId")
        for row in cursor.fetchall():
            print(row)

    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
