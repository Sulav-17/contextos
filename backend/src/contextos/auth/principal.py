from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Principal:
    subject: UUID
    email: str | None
    session_id: UUID | None


@dataclass(frozen=True, slots=True)
class ApplicationUser:
    id: UUID
    email: str
    display_name: str | None
    role: str
    status: str
    memory_enabled: bool

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"
