from __future__ import annotations

import sys

from contextos.cli.bootstrap_admin import main as bootstrap_admin_main


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "bootstrap-admin":
        sys.argv = [sys.argv[0], *sys.argv[2:]]
        bootstrap_admin_main()
        return
    raise SystemExit(
        "Usage: python -m contextos.cli bootstrap-admin --auth-user-id UUID --email EMAIL"
    )


if __name__ == "__main__":
    main()
