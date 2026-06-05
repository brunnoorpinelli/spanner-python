"""DML on Cloud Spanner with the native client library (google-cloud-spanner).

The SDK gives you TWO ways to change data. Both are shown below.

1. Mutations (insert / update / delete / insert_or_update)
   - Buffered objects, not SQL. Fastest for straight row writes.
   - No read-on-write, so you cannot say "WHERE Active = true"; you address
     rows by primary key.

2. DML (execute_update with a SQL string)
   - Real SQL run inside a read/write transaction.
   - Use when the change depends on existing data (e.g. a WHERE clause or a
     computed SET).

run_in_transaction handles begin/commit and automatic retries on abort.
"""

from google.cloud import spanner

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PROJECT_ID, INSTANCE_ID, DATABASE_ID


def main():
    client = spanner.Client(project=PROJECT_ID)
    instance = client.instance(INSTANCE_ID)
    database = instance.database(DATABASE_ID)

    # ---- Mutations: INSERT / UPDATE / DELETE by key -----------------------
    with database.batch() as batch:
        batch.insert(
            table="Singers",
            columns=("SingerId", "FirstName", "LastName", "Active"),
            values=[
                (1, "Marc", "Richards", True),
                (2, "Catalina", "Smith", True),
                (3, "Alice", "Trentor", False),
            ],
        )
        batch.update(
            table="Singers",
            columns=("SingerId", "Active"),
            values=[(3, True)],
        )
        batch.delete(
            table="Singers",
            keyset=spanner.KeySet(keys=[(2,)]),
        )
    print("SDK mutations committed.")

    # ---- DML: conditional UPDATE / DELETE inside a transaction ------------
    def apply_dml(transaction):
        rows = transaction.execute_update(
            "UPDATE Singers SET LastName = 'Anderson' WHERE Active = true"
        )
        print(f"DML updated {rows} row(s).")

        rows = transaction.execute_update(
            "DELETE FROM Singers WHERE Active = false"
        )
        print(f"DML deleted {rows} row(s).")

    database.run_in_transaction(apply_dml)

    # ---- Read back to verify ---------------------------------------------
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(
            "SELECT SingerId, FirstName, LastName, Active FROM Singers ORDER BY SingerId"
        )
        for row in results:
            print(row)


if __name__ == "__main__":
    main()
