from .vc_set import VcSet
from dataclasses import dataclass, field


class AliasUnion:
    def __init__(self):
        self.c_head: set[str] = set()
        self.cv_head: set[str] = set()
        self.c: set[str] = set()
        self.cv: set[str] = set()
        self.vc: VcSet = VcSet()
        self.vcv: VcSet = VcSet()
        self.vr: set[str] = set()
        self.cv_mid: set[str] = set()

        self.is_full_cv: bool = True

        self._set_attribute_list = (
            "c_head",
            "cv_head",
            "c",
            "cv",
            "vc",
            "vcv",
            "vr",
            "cv_mid",
        )

    def update(self, other: "AliasUnion") -> None:
        for attr in self._set_attribute_list:
            updated = getattr(self, attr) | getattr(other, attr)
            self.__setattr__(attr, updated)
        self.is_full_cv = other.is_full_cv

    def difference_update(self, other: "AliasUnion") -> None:
        for attr in self._set_attribute_list:
            updated = getattr(self, attr) - getattr(other, attr)
            self.__setattr__(attr, updated)
        self.is_full_cv = other.is_full_cv

    def copy(self) -> "AliasUnion":
        copy = AliasUnion()
        copy.update(self)
        return copy

    def clear(self) -> None:
        for attr in self._set_attribute_list:
            self[attr].clear()
        self.is_full_cv = True

    def __getitem__(self, key: str) -> set[str] or VcSet:
        return self.__getattribute__(key)

    def __str__(self) -> str:
        return (
            ", ".join(f"{key}={getattr(self, key)}" for key in self._set_attribute_list)
            + " "
            + f"is_full_cv={self.is_full_cv}"
        )
