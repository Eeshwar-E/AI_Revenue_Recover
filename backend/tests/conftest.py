"""Pytest bootstrap: isolate tests on a throwaway SQLite file.

The app suite uses drop_all/create_all, which must NEVER touch the dev
database (backend/revenue_recover.db). Setting DATABASE_URL here (imported
before any app module) binds the engine to a temp file instead.
"""
import os
import tempfile

_fd, _path = tempfile.mkstemp(prefix="rr_test_", suffix=".db")
os.close(_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{_path}"
