from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class Event:
    """Immutable event payload shared between dispatchers and listeners."""

    name: str
    
    payload: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] | None = None
    source: Any | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def with_update(self, **changes: Any) -> Event:
        """Return a copy of the event with the provided field updates applied."""
        return replace(self, **changes)

    def derive(self, name: str | None = None, **changes: Any) -> Event:
        """Copy the event, optionally overriding the name and additional fields."""
        if name is not None:
            changes.setdefault("name", name)
        return self.with_update(**changes)
