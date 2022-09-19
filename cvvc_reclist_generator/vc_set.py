from collections import Counter
from typing import Counter, Iterable, Optional, Iterator
from .errors import PopError


class VcSet:
    """a set to store vc like components and recording max value according to v or c."""

    def __init__(self, vc_likes: Optional[Iterable[tuple[str, str]]] = None):
        self._data: set[tuple[str, str]] = set()
        self._v_counter: Counter[str] = Counter()
        self._c_counter: Counter[str] = Counter()

        if vc_likes:
            self.update(vc_likes)

    @property
    def max_v(self) -> tuple[str, int]:
        return self._v_counter.most_common(1)[0]

    @property
    def max_c(self) -> tuple[str, int]:
        return self._c_counter.most_common(1)[0]

    def update(self, vc_likes: Iterable[tuple[str, str]]) -> None:
        for vc in vc_likes:
            self.add(vc)

    def add(self, vc: tuple[str, str]) -> None:
        if vc not in self:
            self._data.add(vc)
            self._update_counter(vc, True)

    def discard(self, vc: tuple[str, str]) -> None:
        if vc in self:
            self._data.discard(vc)
            self._update_counter(vc, False)

    def pop(self) -> tuple[str, str]:
        if not self:
            raise KeyError("pop from an empty set")

        vc = self._data.pop()
        self._update_counter(vc, False)
        return vc

    def pop_by(self, v: Optional[str]=None, c: Optional[str]=None) -> tuple[str, str]:
        """pop vc with given v and c"""
        for vc in self._data:
            if v and vc[0] == v:
                self.discard(vc)
                return vc

            if c and vc[1] == v:
                self.discard(vc)
                return vc

        raise PopError(f"not found")

    def copy(self) -> "VcSet":
        return VcSet(self._data)

    def difference_update(self, other: "VcSet") -> None:
        while other:
            self.discard(other.pop())
            
    def clear(self) -> None:
        self._data.clear()
        self._v_counter.clear()
        self._c_counter.clear()

    def _update_counter(self, vc: tuple[str, str], is_add: bool) -> None:
        v, c = vc
        if is_add:
            self._v_counter[v] += 1
            self._c_counter[c] += 1
        else:
            self._v_counter[v] -= 1
            self._c_counter[c] -= 1

    def __sub__(self, other: "VcSet") -> "VcSet":
        return VcSet(self._data - other._data)

    def __or__(self, other: "VcSet") -> "VcSet":
        return VcSet(self._data | other._data)
    
    def __len__(self) -> int:
        return len(self._data)
    
    def __iter__(self) -> Iterator[tuple[str, str]]:
        return iter(self._data)

    def __str__(self) -> str:
        return f"VcSet: {self._data}"

    def __contains__(self, vc: tuple[str, str]) -> bool:
        return vc in self._data

    def __bool__(self) -> bool:
        return bool(self._data)
