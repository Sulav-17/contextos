from __future__ import annotations

from redis import Redis
from rq import Worker

from contextos.core.config import get_settings
from contextos.core.logging import configure_logging


def main() -> None:
    settings = get_settings()
    configure_logging(log_level=settings.log_level, log_format=settings.log_format)
    redis = Redis.from_url(settings.redis_url.get_secret_value())
    worker = Worker([settings.document_queue_name], connection=redis)
    worker.work()


if __name__ == "__main__":
    main()
