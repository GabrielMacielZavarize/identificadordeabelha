from __future__ import annotations

from beeai.core.config import get_settings
from beeai.db.session import init_db


def main() -> None:
    settings = get_settings()
    init_db(settings)
    print(f"Database initialized at {settings.database_url}")


if __name__ == "__main__":
    main()
