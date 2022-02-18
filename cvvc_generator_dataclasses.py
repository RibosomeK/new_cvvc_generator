from collections import namedtuple, Counter
from enum import Enum
from typing import Counter, Set, Optional, Iterable
from dataclasses import dataclass, field


Alias_Type = Enum('Alias_Type', 'C CV VC VCV VR')


class CVV(namedtuple("CVV", "cvv c v act_c fol_v cv mid_v end_v")):
    """
    take [gwaang] for example:
        cvv: gwaang
        c: k
        v: aang
        acl_c: khw (actual consonant)
        cv: gwA (does not include end_v)
        mid_v: aang (stretch part in lengthening a note)
        end_v: ng (the ended part)
    last three params are optional (None),
    but one is filled, all three of them must be filled.
    """

    __slot__ = ()
    
    @staticmethod
    def new(components: Optional[Iterable[str]]=None) -> 'CVV':
        length = 8
        if components is None:
            return CVV(*[None]*length)
        else:
            param = []
            for idx, value in enumerate(components):
                if idx > length:
                    raise SyntaxError(f'More than {length} arguments are given.')
                if value == '':
                    value = None
                param.append(value)
            param.extend([None]*(length - len(param)))
            return CVV(*param)
    
    def get_cv(self, is_full_cv: Optional[bool] = True) -> str:
        if is_full_cv:
            return self.cvv
        else:
            return self.cv if self.cv else self.cvv
        
    def get_lsd_c(self) -> str:
        return self.act_c if self.act_c is not None else self.c
    
    def get_lsd_v(self) -> str:
        return self.fol_v if self.fol_v is not None else self.v
        
    def get_lsd_cvv(self) -> tuple[str, str, str]:
        cvv = self.get_cv()
        c = self.get_lsd_c()
        v = self.get_lsd_v()
        return (cvv, c, v)

    def __str__(self) -> str:
        str_order = (self.cvv, self.cv, 
                     self.c, self.v, self.act_c, 
                     self.fol_v, self.mid_v, self.end_v)
        for value in str_order:
            if value:
                return str(value)
        else:
            return 'R'

    def __bool__(self) -> bool:
        for ele in self:
            if ele:
                return True
        else:
            return False


class RecLine(tuple[CVV, ...]):
    def __new__(cls, *args):
        recline = (x for x in args)
        return super().__new__(cls, recline)

    def __str__(self, split_symbol: str = "_") -> str:
        if isinstance(self[0], CVV):
            line: str = split_symbol + split_symbol.join(str(e) for e in self)
        else:
            line: str = split_symbol.join(str(e) for e in self)
        if "R" in line or line.islower():
            return line
        else:
            return f"{line}_UpperCase"


class OTO(namedtuple("OTO", "wav prefix alias suffix l con r pre ovl")):
    __slot__ = ()

    def __str__(self) -> str:
        alias = self.alias
        if self.prefix:
            alias = self.prefix + self.alias
        if self.suffix:
            alias += self.suffix
        return "{}={},{},{},{},{},{}".format(self.wav, alias, *self[-5:])
    

class VS_OTO(namedtuple("VS_OTO", "phoneme wav l pre con r ovl")):
    __slot__ = ()
    
    def __str__(self) -> str:
        return ','.join(str(ele) for ele in self)
    
    @staticmethod
    def get_redirect(phoneme: str, redirect_phoneme: str) -> "VS_OTO":
        return VS_OTO(phoneme, f'#{redirect_phoneme}', 0, 0, 0, 0, 0)


class VC_Set(set[tuple[str, str]]):
    _v_counter: Counter
    _c_counter: Counter
    __max_v: tuple[str, int] = ("", 0)
    __max_c: tuple[str, int] = ("", 0)

    def __init__(self, __iterable: Iterable[tuple[str, str]] = ...) -> None:
        if __iterable == ...:
            __iterable = set()
        super().__init__(__iterable)
        self.__post_init__()

    def __post_init__(self) -> None:
        self._v_counter = Counter()
        self._c_counter = Counter()
        for vc in self:
            self.__update_dict(vc, True)

    @property
    def max_v(self):
        self.__max_v = self._v_counter.most_common(1)[0]
        return self.__max_v

    @property
    def max_c(self):
        self.__max_c = self._c_counter.most_common(1)[0]
        return self.__max_c
        
        
    def __update_dict(self, vc: tuple[str, str], is_add: bool) -> None:
        update_idx = 1 if is_add else -1
        v, c = vc
        self._v_counter[v] += update_idx
        self._c_counter[c] += update_idx

    def add(self, vc: tuple[str, str]) -> None:
        self.__update_dict(vc, True)
        return super().add(vc)

    def update(self, __iterable: Iterable[tuple[str, str]]) -> None:
        for value in __iterable:
            self.add(value)

    def discard(self, vc: tuple[str, str]) -> None:
        if vc not in self:
            return
        self.__update_dict(vc, False)
        return super().discard(vc)

    def pop(self, c: Optional[str] = None, v: Optional[str] = None) -> tuple[str, str]:
        if not (c or v):
            vc = super().pop()
            self.__update_dict(vc, False)
            return vc
        aimed_vc = None
        for vc in self:
            if c and c == vc[1]:
                aimed_vc = vc
            elif v and v == vc[0]:
                aimed_vc = vc
            if aimed_vc:
                break
        if aimed_vc:
            self.discard(aimed_vc)
            return aimed_vc
        else:
            raise ValueError

    def __sub__(self, __iterable: Iterable[tuple[str, str]]) -> "VC_Set":
        for value in __iterable:
            self.discard(value)
        return self
    
    def __or__(self, __iterable: Iterable[tuple[str, str]]) -> "VC_Set":
        for value in __iterable:
            self.add(value)
        return self
    
    def copy(self) -> "VC_Set":
        new_vc_set = VC_Set()
        new_vc_set.update(self)
        return new_vc_set


@dataclass
class AliasUnion:
    c_head: Set[str] = field(default_factory=set)
    cv_head: Set[str] = field(default_factory=set)
    cv: Set[str] = field(default_factory=set)
    vc: VC_Set = field(default_factory=VC_Set)
    vr: Set[str] = field(default_factory=set)
    vcv: VC_Set = field(default_factory=VC_Set)

    def __len__(self) -> int:
        return len(self.__dict__)

    def __getitem__(self, key: str) -> set | VC_Set:
        return self.__dict__[key]

    def __iter__(self):
        for values in self.__dict__.values():
            yield values

    def __bool__(self) -> bool:
        for container in self:
            if container:
                return True
        else:
            return False
        
    def copy(self) -> "AliasUnion":
        union = AliasUnion()
        for key in self.__dict__:
            union.__dict__[key] = self.__dict__[key].copy()
        return union

    def __repr__(self) -> str:
        return ", ".join(f"{key}={value}" for key, value in self.__dict__.items())

    def add(self, other: "AliasUnion") -> None:
        for key, value in other.__dict__.items():
            self.__dict__[key].__or__(value)

    def discard(self, other: "AliasUnion") -> None:
        for key, value in other.__dict__.items():
            self.__dict__[key].__sub__(value)
