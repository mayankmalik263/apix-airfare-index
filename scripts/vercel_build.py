"""Vercel build step: bootstrap the database, then bake in one operator account.

    python -m scripts.vercel_build

The function's filesystem is read-only at runtime and the app serves a /tmp
copy of apix.db, so anything written at runtime dies with the instance. The
admin account therefore has to exist in the file that ships: it is created
here from APIX_ADMIN_EMAIL / APIX_ADMIN_PASSWORD when both are set.
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apix.config import db_path  # noqa: E402
from scripts import bootstrap  # noqa: E402
from webapp.backend import auth  # noqa: E402


def main() -> int:
    bootstrap.main()

    conn = sqlite3.connect(db_path())
    email = os.environ.get("APIX_ADMIN_EMAIL", "").strip()
    password = os.environ.get("APIX_ADMIN_PASSWORD", "")
    if email and password:
        if not auth.set_password(conn, email, password):
            auth.create_user(conn, email, email.split("@")[0], password, "admin")
        print(f"  operator account ready: {email}")
    else:
        print("  APIX_ADMIN_EMAIL / APIX_ADMIN_PASSWORD not set: no operator "
              "account, /console will not accept a sign-in")
    # Fold the WAL back into the main file: only apix.db is copied at runtime.
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
