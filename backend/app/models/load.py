from dataclasses import dataclass


@dataclass(frozen=True)
class LoadProfile:
    critical_kw: float
    total_kw: float
    flexible_kw: float
