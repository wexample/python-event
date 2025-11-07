from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ListenerSpec:
    name: str
    priority: int
    once: bool
