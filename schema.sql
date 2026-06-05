-- Shared schema used by all three samples.
-- Apply with the gcloud CLI before running anything that touches Spanner:
--
--   gcloud spanner databases ddl update example-db \
--     --instance=example-instance \
--     --ddl-file=schema.sql
--
-- (Each statement below can also be pasted into the Cloud Console DDL editor.)

CREATE TABLE Singers (
  SingerId   INT64 NOT NULL,
  FirstName  STRING(1024),
  LastName   STRING(1024),
  Active     BOOL,
) PRIMARY KEY (SingerId);
