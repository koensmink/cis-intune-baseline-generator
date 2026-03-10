from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import IntuneMapping, NormalizedControl


class MappingRule(ABC):
    rule_id: str

    @abstractmethod
    def matches(self, control: NormalizedControl) -> bool:
        raise NotImplementedError

    @abstractmethod
    def apply(self, control: NormalizedControl) -> IntuneMapping:
        raise NotImplementedError
