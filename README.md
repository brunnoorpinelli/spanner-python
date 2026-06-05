# Cloud Spanner DML in Python — Three Ways

Three self-contained samples showing how to run **DML** (INSERT / UPDATE / DELETE)
against [Google Cloud Spanner](https://cloud.google.com/spanner) from Python, each
using a different layer of abstraction.

| # | Method | Library | You write… | Best when… |
|---|--------|---------|------------|------------|
| 1 | [Raw SQL (DB-API)](dbapi_sql/dml_dbapi.py) | `google-cloud-spanner` (DB-API / PEP 249) | SQL strings | you want plain SQL with no framework |
| 2 | [Native SDK](spanner_sdk/dml_sdk.py) | `google-cloud-spanner` | mutations **or** SQL | you want full control + Spanner-specific features |
| 3 | [SQLAlchemy ORM](sqlalchemy_orm/dml_sqlalchemy.py) | `sqlalchemy-spanner` | Python objects | you want portable, framework-style data access |

---

## The three methods compared

### 1. Raw SQL via the DB-API
The DB-API connection is bundled inside `google-cloud-spanner`. You get a standard
`connect()` → `cursor.execute(sql, params)` → `commit()` flow — identical in shape
to `sqlite3` or `psycopg2`. Plain raw-SQL access, pure Python.

```python
cursor.execute(
    "UPDATE Singers SET Active = %(active)s WHERE SingerId = %(id)s",
    {"active": True, "id": 3},
)
connection.commit()
```

**Pros**
- Zero framework — just SQL strings and a cursor; flat learning curve.
- Parameterized queries guard against SQL injection.
- Familiar PEP 249 shape (`sqlite3` / `psycopg2`), easy to drop into scripts.

**Cons**
- No object mapping — you hand-write every SQL string and map rows yourself.
- Not portable — Spanner SQL dialect is baked into your strings.
- Manual `commit()` / `rollback()` and transaction handling.
- Bypasses Spanner-specific perf paths like mutations (method 2).

### 2. Native SDK
The client library exposes two write styles:
- **Mutations** — buffered insert/update/delete by primary key. No SQL, fastest path.
- **DML** — `transaction.execute_update("UPDATE …")` for changes that depend on a
  `WHERE` clause or computed values.

```python
# Mutation insert — columns once, then one tuple per row
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

# DML for conditional changes
def apply_dml(transaction):
    transaction.execute_update("UPDATE Singers SET LastName = 'Anderson' WHERE Active = true")

database.run_in_transaction(apply_dml)   # begin + commit + retry handled for you
```

**Pros**
- Full access to Spanner features — mutations, partitioned DML, stale reads.
- Mutations are the fastest write path for straight key-based row changes.
- `run_in_transaction` handles begin/commit and automatic retry on abort.
- Official, first-party library — best support and docs.

**Cons**
- Spanner-only API; code does not transfer to other databases.
- More verbose — two write styles (mutations vs DML) to learn when to use.
- No object mapping; you work with column tuples / rows.

### 3. SQLAlchemy ORM
Map tables to classes, then add/change/delete objects through a `Session`. Most
portable — switch databases by changing the connection URL.

```python
singer = session.get(Singer, 3)
singer.Active = True
session.commit()
```

**Pros**
- Portable — same model code targets PostgreSQL, MySQL, etc. by swapping the URL.
- Object mapping — work with Python objects, no hand-written SQL or row parsing.
- Rich ecosystem: relationships, migrations (Alembic), query builder.
- Familiar to teams already using SQLAlchemy.

**Cons**
- Extra dependency + abstraction layer to learn and debug.
- Dialect lags the native SDK; some Spanner features unsupported or awkward.
- ORM overhead and hidden SQL can mask performance issues at scale.
- No auto-increment on Spanner — you still assign primary keys manually.

---

## Prerequisites

- Python 3.9+
- A Cloud Spanner instance + database ([quickstart](https://cloud.google.com/spanner/docs/quickstart-console))
- Authentication via [Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc):
  ```bash
  gcloud auth application-default login
  ```

## Setup

```bash
pip install -r requirements.txt

# Apply the shared table (see schema.sql)
gcloud spanner databases ddl update example-db \
  --instance=example-instance \
  --ddl-file=schema.sql
```

Point the samples at your instance via environment variables (or edit
[`config.py`](config.py)):

```bash
export SPANNER_PROJECT_ID=your-gcp-project
export SPANNER_INSTANCE_ID=example-instance
export SPANNER_DATABASE_ID=example-db
```

## Run

```bash
python dbapi_sql/dml_dbapi.py
python spanner_sdk/dml_sdk.py
python sqlalchemy_orm/dml_sqlalchemy.py
```

All three operate on the same `Singers` table (defined in [`schema.sql`](schema.sql))
and perform the same INSERT / UPDATE / DELETE sequence, then print the result.

> The samples are **illustrative**: they show the API surface clearly. Run them
> against a throwaway database — each one writes and deletes rows.

## Layout

```
.
├── README.md
├── requirements.txt
├── schema.sql            # shared Singers table
├── config.py             # project / instance / database IDs
├── dbapi_sql/            # method 1 — raw SQL via DB-API
├── spanner_sdk/          # method 2 — native client (mutations + DML)
└── sqlalchemy_orm/       # method 3 — SQLAlchemy ORM
```

## License

MIT
