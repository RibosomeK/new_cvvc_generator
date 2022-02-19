import configparser
from dataclasses import dataclass, field
from enum import Enum
from typing import Counter, Iterable, Optional
from cvv_workshop import CvvWorkshop, Cvv


class AliasType(Enum):
    C = 'C'
    CV = 'CV'
    VC = 'VC'
    VCV = 'VCV'
    VR = 'VR'
    
    
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
    c_head: set[str] = field(default_factory=set)
    cv_head: set[str] = field(default_factory=set)
    cv: set[str] = field(default_factory=set)
    vc: VC_Set = field(default_factory=VC_Set)
    vr: set[str] = field(default_factory=set)
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


class AliasUnionGenerator:
    """get needed alias."""
    
    def __init__(self, dict_dir: str) -> None:
        self.cvv_workshop = CvvWorkshop()
        self.cvv_workshop.read_dict(dict_dir)
    
    def get_needed_alias(self, is_c_head: bool = False, is_cv_head: bool = True, is_full_cv: bool = True, alias_config: Optional[str] = None) -> 'AliasUnion':
        """Get needed alias.

        Args:
            c_head (bool, optional): Begining consonant for vocalsharp. Defaults to False.
            cv_head (bool, optional): Begining cv head. Defaults to True.
            is_full_cv (bool, optional): For cv and cv head. 
                If your dict included extra cv part and you WANT TO use them in non vcv part,
                you must set to False. Defaults to True.
            alias_config (Optional[str], optional): exceptional alias config. Defaults to None.

        Returns:
            AliasUnion
        """
        alias_union = AliasUnion()
        if is_c_head:
            alias_union.c_head = {
                x.get_lsd_c() 
                for x in self.cvv_workshop.cvv_set
                if x.v != x.get_lsd_c()
            }
        alias_union.cv = {cv.get_cv(is_full_cv) for cv in self.cvv_workshop.cvv_set}
        if is_cv_head:
            alias_union.cv_head = alias_union.cv.copy()
        alias_union.vc = VC_Set()
        alias_union.vc.update(
            (v, c) 
            for v in self.cvv_workshop.v_dict
            for c in self.cvv_workshop.c_dict
        )
        alias_union.vr = {v for v in self.cvv_workshop.v_dict}
        if alias_config:
            unneeded, needed = self.read_alias_config(alias_config)
            alias_union.add(needed)
            alias_union.discard(unneeded)
        if alias_union.vcv:
            alias_union.vcv = alias_union.vcv - alias_union.vc
        self.alias = alias_union
        return alias_union

    def read_alias_config(self, alias_config: str, is_full_cv: bool = True) -> tuple[AliasUnion, AliasUnion]:
        """Read alias config to get unwanted alias and wanted alias.
        For config format plz check on the comments in config

        Args:
            alias_config (str): config path.
            is_full_cv (bool): For cv and cv head. Details in self.get_needed_alias()

        Raises:
            ValueError: Given a wrong value like there is no 'R' but get one. 

        Returns:
            tuple[unneeded_AliasUnion, needed_AliasUnion]
        """
        unneeded, needed = AliasUnion(), AliasUnion()
        config = configparser.ConfigParser()
        config.read(alias_config, encoding="utf-8")
        for key, value in config["UNNEEDED"].items():
            if not value or value.upper() == "NONE":
                continue
            if key == "cv_head" or key == "cv":
                for cv in value.split(","):
                    if self.cvv_workshop.find_cvv(cvv=cv):
                        unneeded.__dict__[cv].add(cv)
                    elif cv in self.cvv_workshop.c_dict:
                        unneeded.__dict__[cv].update(
                            cvv.get_cv(is_full_cv) for cvv in self.cvv_workshop.c_dict[cv]
                        )
                    else:
                        raise ValueError
            elif key == "vc":
                for vc in value.split(","):
                    if vc in self.cvv_workshop.c_dict:
                        unneeded.vc.update((v, vc) for v in self.cvv_workshop.v_dict)
                    if vc in self.cvv_workshop.v_dict:
                        unneeded.vc.update((vc, c) for c in self.cvv_workshop.c_dict)
                    elif " " in vc:
                        unneeded.vc.add(tuple(vc.split(" ")))
                    else:
                        raise ValueError
            elif key == "vr":
                unneeded.vr.update(value.split(","))
            elif key == "c_head":
                unneeded.c_head.update(value.split(","))
            elif key == "vcv":
                for vcv in value.split(","):
                    if vcv in self.cvv_workshop.c_dict:
                        unneeded.vcv.update(
                            (v, cvv.get_cv())
                            for v in self.cvv_workshop.v_dict
                            for cvv in self.cvv_workshop.c_dict[vcv]
                        )
                    elif vcv in self.cvv_workshop.v_dict:
                        unneeded.vcv.update(
                            (vcv, cvv.get_cv()) 
                            for cvv in self.cvv_workshop.cvv_set
                        )
                    elif " " in vcv:
                        unneeded.vcv.add(tuple(vcv.split(" ")))
        vcv_value = config["NEEDED"]["vcv"]
        if vcv_value.upper() == "ALL":
            needed.vcv.update(
                (v, cvv.get_cv()) 
                for v in self.cvv_workshop.v_dict
                for cvv in self.cvv_workshop.cvv_set
            )
        elif "," in vcv_value:
            for vcv in vcv_value.split(","):
                if vcv in self.cvv_workshop.c_dict:
                    needed.vcv.update(
                        (v, cvv.get_cv())
                        for v in self.cvv_workshop.v_dict
                        for cvv in self.cvv_workshop.c_dict[vcv]
                    )
                elif vcv in self.cvv_workshop.v_dict:
                    needed.vcv.update(
                        (vcv, cvv.get_cv()) 
                        for cvv in self.cvv_workshop.cvv_set
                    )
                elif " " in vcv:
                    needed.vcv.add(tuple(vcv.split(" ")))
        return unneeded, needed
