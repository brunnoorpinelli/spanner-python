"""Shared connection identifiers.

Illustrative placeholders — override via environment variables, or just edit the
defaults below to point at your own instance/database.
"""

import os

PROJECT_ID = os.environ.get("SPANNER_PROJECT_ID", "your-gcp-project")
INSTANCE_ID = os.environ.get("SPANNER_INSTANCE_ID", "example-instance")
DATABASE_ID = os.environ.get("SPANNER_DATABASE_ID", "example-db")
