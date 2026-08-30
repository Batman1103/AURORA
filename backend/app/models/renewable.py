from dataclasses import dataclass


@dataclass(frozen=True)
class RenewableAsset:
    source: str
    capacity_kw: float
