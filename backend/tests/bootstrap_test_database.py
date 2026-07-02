from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from tests.support import ensure_test_database

ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
BACKEND_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


def main() -> None:
    load_dotenv(ROOT_ENV_FILE, override=False)
    load_dotenv(BACKEND_ENV_FILE, override=False)
    ensure_test_database()


if __name__ == "__main__":
    main()
