from collections import namedtuple, deque
from random import choice
from typing import List, Set, Dict, Optional, Iterable
from dataclasses import dataclass, field
import configparser


class CVV(namedtuple("CVV", "cvv c v act_c cv mid_v end_v")):
    """
    take [gwaang] for exsample:
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

    def __str__(self) -> str:
        str_order = (self.cvv, self.cv, 
                     self.c, self.v, self.act_c, 
                     self.mid_v, self.end_v)
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


class RecLine(tuple):
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


class OTO(namedtuple("OTO", "wav prefix alien suffix l con r pre ovl")):
    __slot__ = ()

    def __str__(self) -> str:
        alien = self.alien
        if self.prefix:
            alien = self.prefix + self.alien
        if self.suffix:
            alien += self.suffix
        return "{}={},{},{},{},{},{}".format(self.wav, alien, *self[-5:])


"""class AliensType(Enum):
    _c = auto()
    c = auto()
    _cv = auto()
    cv = auto()
    vc = auto()
    v = auto()
    vcv = auto()"""


class VC_Set(set[tuple[str, str]]):
    v_dict: Dict[str, int]
    c_dict: Dict[str, int]
    __max_v: tuple[str, int] = ("", 0)
    __max_c: tuple[str, int] = ("", 0)

    def __init__(self, __iterable: Iterable[tuple[str, str]] = ...) -> None:
        if __iterable == ...:
            __iterable = set()
        super().__init__(__iterable)
        self.__post_init__()

    def __post_init__(self) -> None:
        self.v_dict = {}
        self.c_dict = {}
        for vc in self:
            self.__update_dict(vc, True)

    @property
    def max_v(self):
        return self.__max_v

    @max_v.setter
    def max_v(self, value: tuple[str, int]):
        self.__max_v = value

    @property
    def max_c(self):
        return self.__max_c

    @max_c.setter
    def max_c(self, value: tuple[str, int]):
        self.__max_c = value

    def find_max(self, aliens_type: str) -> tuple[str, int]:
        if self is None:
            raise IndexError
        if aliens_type not in ["v", "c"]:
            raise TypeError
        current_max_digit, current_max_letter = 0, ""
        
        if aliens_type == 'v':
            max_v = max(self.v_dict, key=lambda k: self.v_dict[k])
            current_max_letter, current_max_digit = max_v, self.v_dict[max_v]
        elif aliens_type == 'c':
            max_c = max(self.c_dict, key=lambda k: self.c_dict[k])
            current_max_letter, current_max_digit = max_c, self.c_dict[max_c]
            
        if current_max_digit == 0:
            return ('', 0)
        else:
            return (current_max_letter, current_max_digit)
        
        '''if aliens_type == "v":
            for key, value in self.v_dict.items():
                if value > current_max_digit:
                    current_max_digit = value
                    current_max_letter = key
        elif aliens_type == "c":
            for key, value in self.c_dict.items():
                if value > current_max_digit:
                    current_max_digit = value
                    current_max_letter = key
        return (current_max_letter, current_max_digit)
        if current_max_digit == 0 or current_max_letter == '':
            self.__post_init__()
            if aliens_type == 'v':
                return self.__max_v
            else:
                return self.__max_c
        else:
            return (current_max_letter, current_max_digit)'''

    def __update_dict(self, vc: tuple[str, str], add_or_sub: bool) -> None:
        update_idx = 1 if add_or_sub else -1
        v, c = vc
        if add_or_sub:
            self.v_dict.setdefault(v, 0)
            self.c_dict.setdefault(c, 0)
        self.v_dict[v] += update_idx
        self.c_dict[c] += update_idx
        if add_or_sub:
            if self.v_dict[v] > self.max_v[1]:
                self.__max_v = (v, self.v_dict[v])
            if self.c_dict[c] > self.max_c[1]:
                self.__max_c = (c, self.c_dict[c])
        else:
            if v == self.max_v[0]:
                self.__max_v = self.find_max("v")
            if c == self.max_c[0]:
                self.__max_c = self.find_max("c")

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


@dataclass
class Aliens:
    _c: Set[str] = field(default_factory=set)
    _cv: Set[str] = field(default_factory=set)
    cv: Set[str] = field(default_factory=set)
    vc: VC_Set = field(default_factory=VC_Set)
    vr: Set[str] = field(default_factory=set)
    vcv: VC_Set = field(default_factory=VC_Set)

    def __post_init__(self) -> None:
        self._c = set()
        self._cv = set()
        self.cv = set()
        self.vc = VC_Set()
        self.vr = set()
        self.vcv = VC_Set()

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

    def __repr__(self) -> str:
        return ", ".join(f"{key}={value}" for key, value in self.__dict__.items())

    def add(self, other: "Aliens") -> None:
        for key, value in other.__dict__.items():
            self.__dict__[key] |= value

    def discard(self, other: "Aliens") -> None:
        for key, value in other.__dict__.items():
            self.__dict__[key] -= value


class CVVCReclistGenerator:
    def __init__(self) -> None:
        self.cvv: Set[CVV] = set()
        self.cvv_dict: Dict[str, CVV] = {}
        self.c_dict: Dict[str, List[CVV]] = {}
        self.v_dict: Dict[str, List[CVV]] = {}

        self.reclist: List[RecLine] = []
        self.oto: List[OTO] = []

        self.aliens: Aliens
        self.emptyCVV = CVV(*[None] * 7)

    def read_dict(self, dict_dir: str) -> None:
        """read a cvvc dict in the following format:
            bao,p,ao
            pao,ph,ao
            ...
            guang,k,uang
            kuang,kh,uang
        split symbol \t can also be used
        the format can be also extend for more detail structue of the word,
        more specific can be seen in OTO class

        Args:
            dict_dir (str): the path of dict file

        Raises:
            SyntaxError: more than 7 elements are given

        [Todo]:
            comment support, both multipul lines and single
        """
        with open(dict_dir, mode="r", encoding="utf-8") as dict_file:
            dict_content = dict_file.read()

        for line in dict_content.splitlines():
            if line:
                if "," in line:
                    cvv, c, v, *_ = line.split(",")
                elif "\t" in line:
                    cvv, c, v, *_ = line.split("\t")
                else:
                    raise SyntaxError
                if _:
                    word = CVV(cvv, c, v, *_)
                else:
                    word = CVV(cvv, c, v, None, None, None, None)
                self.cvv.add(word)
                self.cvv_dict.setdefault(cvv, word)
                self.c_dict.setdefault(c, []).append(word)
                self.v_dict.setdefault(v, []).append(word)

    def find_cvv(
        self,
        cvv: str = None,
        c: str = None,
        v: str = None,
        exception: Optional[Set[str]] = None,
    ) -> CVV:
        """find a cvv class by a cvv, c, or v

        Returns:
            [CVV]: [description]
        """
        if cvv:
            if cv := self.cvv_dict.get(cvv):
                return cv
            else:
                for ele in list(self.cvv):
                    if ele.cv == cvv:
                        return ele
                else:
                    raise ValueError
        if c and not v:
            if cvv_list := self.c_dict.get(c):
                if exception:
                    new_cvv_list: List[CVV] = []
                    for cv in cvv_list:
                        if cv.v not in exception:
                            new_cvv_list.append(cv)
                    cvv_list = new_cvv_list
                if not cvv_list:
                    raise ValueError
                return choice(cvv_list)
        if v and not c:
            if cvv_list := self.v_dict.get(v):
                if exception:
                    new_cvv_list: List[CVV] = []
                    for cv in cvv_list:
                        if cv.c not in exception:
                            new_cvv_list.append(cv)
                    cvv_list = new_cvv_list
                if not cvv_list:
                    raise ValueError
                return choice(cvv_list)
        if c and v:
            if cvv_list := self.c_dict.get(c):
                for cv in cvv_list:
                    if cv.v == v:
                        return cv
                else:
                    raise ValueError
        raise SyntaxError

    def get_needed_aliens(
        self,
        _c: bool = False,
        _cv: bool = True,
        full_cv: bool = True,
        aliens_config: Optional[str] = None,
    ) -> Aliens:
        aliens = Aliens()
        if _c:
            aliens._c = {x for x in self.c_dict.keys()}
        if full_cv:
            aliens.cv = {x.cvv for x in self.cvv}
        else:
            for cv in self.cvv:
                cv = cv.cv
                if cv is None:
                    raise TypeError
                else:
                    aliens.cv.add(cv)
        if _cv:
            aliens._cv = aliens.cv.copy()
        aliens.vc = VC_Set()
        aliens.vc.update((v, c) for v in self.v_dict.keys() for c in self.c_dict.keys())
        aliens.vr = {v for v in self.v_dict.keys()}
        if aliens_config:
            unneeded, needed = self.read_aliens_config(aliens_config)
            aliens.add(needed)
            aliens.discard(unneeded)
        if aliens.vcv:
            aliens.vcv = aliens.vcv - aliens.vc
        self.aliens = aliens
        return aliens

    def read_aliens_config(self, aliens_config: str) -> tuple[Aliens, Aliens]:
        unneeded, needed = Aliens(), Aliens()
        config = configparser.ConfigParser()
        config.read(aliens_config, encoding="utf-8")
        for key, value in config["UNNEEDED"].items():
            if not value or value.upper() == "NONE":
                continue
            if key == "_cv" or key == "cv":
                for cv in value.split(","):
                    if self.find_cvv(cvv=cv):
                        unneeded.__dict__[cv].add(cv)
                    elif cv in self.c_dict.keys():
                        unneeded.__dict__[cv].update(
                            (cvv.cvv for cvv in self.c_dict[cv])
                        )
                        unneeded.__dict__[cv].update(
                            (cvv.cv for cvv in self.c_dict[cv] if cvv.cv is not None)
                        )
                    else:
                        raise ValueError
            elif key == "vc":
                for vc in value.split(","):
                    if vc in self.v_dict.keys():
                        unneeded.vc.update((vc, c) for c in self.c_dict.keys())
                    elif " " in vc:
                        unneeded.vc.add(tuple(vc.split(" ")))
                    else:
                        raise ValueError
            elif key == "vr":
                unneeded.vr.update(value.split(","))
            elif key == "_c":
                unneeded._c.update(value.split(","))
            elif key == "vcv":
                for vcv in value.split(","):
                    if vcv in self.c_dict.keys():
                        unneeded.vcv.update(
                            (v, cvv.cvv)
                            for v in self.v_dict.keys()
                            for cvv in self.c_dict[vcv]
                        )
                        unneeded.vcv.update(
                            (v, cvv.cv)
                            for v in self.v_dict.keys()
                            for cvv in self.c_dict[vcv]
                            if cvv.cv is not None
                        )
                    elif vcv in self.v_dict.keys():
                        unneeded.vcv.update((vcv, cvv) for cvv in self.cvv_dict.keys())
                        unneeded.vcv.update(
                            (vcv, cvv.cv) for cvv in self.cvv if cvv.cv is not None
                        )
                    elif " " in vcv:
                        unneeded.vcv.add(tuple(vcv.split(" ")))
        vcv_value = config["NEEDED"]["vcv"]
        if vcv_value.upper() == "ALL":
            needed.vcv.update(
                (v, cvv) for v in self.v_dict.keys() for cvv in self.cvv_dict.keys()
            )
            needed.vcv.update(
                (v, cvv.cv)
                for v in self.v_dict.keys()
                for cvv in self.cvv
                if cvv.cv is not None
            )
        elif "," in vcv_value:
            for vcv in vcv_value.split(","):
                if vcv in self.c_dict.keys():
                    needed.vcv.update(
                        (v, cvv.cvv)
                        for v in self.v_dict.keys()
                        for cvv in self.c_dict[vcv]
                    )
                    needed.vcv.update(
                        (v, cvv.cv)
                        for v in self.v_dict.keys()
                        for cvv in self.c_dict[vcv]
                        if cvv.cv is not None
                    )
                elif vcv in self.v_dict.keys():
                    needed.vcv.update((vcv, cvv) for cvv in self.cvv_dict.keys())
                    needed.vcv.update(
                        (vcv, cvv.cv) for cvv in self.cvv if cvv.cv is not None
                    )
                elif " " in vcv:
                    needed.vcv.add(tuple(vcv.split(" ")))
        return unneeded, needed

    def gen_2mora(self, aliens: Aliens) -> None:
        all_cv = list(aliens.cv | aliens._cv)
        all_vc, all_vcv = aliens.vc, aliens.vcv
        all_cv.sort()
        for cv in all_cv:
            cvv = self.find_cvv(cvv=cv)
            if cvv:
                self.reclist.append(RecLine(cvv, cvv))
                all_vc.discard((cvv.v, cvv.c))
                if all_vcv:
                    all_vcv.discard((cvv.v, cvv.cvv))
                    if cvv.cv:
                        all_vcv.discard((cvv.v, cvv.cv))
            else:
                print(f"{cv}= has no match word.")
                raise ValueError
        all_vc = list(all_vc)
        all_vc.sort()
        for vc in all_vc:
            self.reclist.append(RecLine(*vc))
        if all_vcv:
            all_vcv = list(all_vcv)
            all_vcv.sort()
            for vcv in all_vcv:
                self.reclist.append(RecLine(*vcv))

    def gen_plan_b(self, aliens: Aliens) -> Aliens:
        all_cv = list(aliens.cv | aliens._cv)
        all_cv.sort()
        for cv in all_cv:
            if cv := self.find_cvv(cv):
                self.reclist.append(RecLine(cv, cv, cv))
                aliens.vc.discard((cv.v, cv.c))
                if cv.cv:
                    aliens.cv.discard(cv.cv)
                    aliens._cv.discard(cv.cv)
                aliens.cv.discard(cv.cvv)
                aliens._cv.discard(cv.cvv)
                aliens.vr.discard(cv.v)
                if aliens.vcv:
                    aliens.vcv.discard((cv.v, cv.cvv))
                    aliens.vcv.discard((cv.v, cv.cv))
            else:
                raise ValueError
        return aliens

    def gen_mora_x(
        self, aliens: Aliens, length: int, cv_mid: Optional[Set[str]] = None
    ) -> None:
        if cv_mid is None:
            cv_mid = set()

        cv_deque = deque(sorted(list(aliens.cv)))
        while cv_deque:
            row: List[CVV] = []
            cv_mid_switch = False
            for i in range(length):
                if not cv_deque:
                    break
                if cv_mid_switch:
                    continue
                cv = self.find_cvv(cvv=cv_deque.popleft())
                row.append(cv)
                if i == 0:
                    aliens._cv.discard(cv.cvv)
                    aliens._cv.discard(cv.cv)
                    if (cv.cvv in cv_mid) or (cv.cv in cv_mid):
                        row.append(cv)
                        cv_mid_switch = not cv_mid_switch
                elif i < length - 1:
                    aliens.vc.discard((row[i].v, cv.c))
                    aliens.vcv.discard((row[i].v, cv.cvv))
                    aliens.vcv.discard((row[i].v, cv.cv))
                else:
                    aliens.vr.discard(cv.v)
            self.reclist.append(RecLine(*row))
        aliens.cv.clear()

        # complete the vc part
        def find_next(vc: tuple[str, str], vc_max_v: str) -> CVV:
            try:
                next_cv = self.find_cvv(c=vc[1], v=vc_max_v)
            except ValueError:
                next_cv = self.find_cvv(c=vc[1])
            return next_cv

        row: List[CVV] = []
        i = 0
        while True:
            if not aliens.vc:
                break
            cv_mid_switch = False
            
            if i == 0:
                current_v = aliens.vc.max_v[0]
                current_cv = self.find_cvv(v=current_v)
                current_vc = aliens.vc.pop(v=current_v)
                row.append(current_cv)
                row.append(find_next(current_vc, aliens.vc.max_v[0]))
                i += 2
            elif i <= length - 1:
                try:
                    vc = aliens.vc.pop(v=row[-1].v)
                    row.append(find_next(vc, aliens.vc.max_v[0]))
                    i += 1
                except ValueError:
                    if i <= length - 2:
                        vc = aliens.vc.pop()
                        cv1 = self.find_cvv(v=vc[0])
                        try:
                            cv2 = self.find_cvv(c=vc[1], v=aliens.vc.max_v[0])
                        except ValueError:
                            cv2 = self.find_cvv(c=vc[1])
                        aliens.vcv.discard((row[-1].v, cv1.cvv))
                        aliens.vcv.discard((row[-1].v, cv1.cv))
                        row.extend([cv1, cv2])
                        aliens.vcv.discard((cv1.v, cv2.cvv))
                        aliens.vcv.discard((cv1.v, cv2.cv))
                        i += 2
                    else:
                        i = length
                        continue
                aliens.vcv.discard((row[-2].v, row[-1].cvv))
                aliens.vcv.discard((row[-2].v, row[-1].cv))
            elif i == length:
                self.reclist.append(RecLine(*row))
                aliens.vr.discard(row[-1].v)
                aliens._cv.discard(row[0].cvv)
                aliens._cv.discard(row[0].cv)
                row: List[CVV] = []
                i = 0
        if row:
            self.reclist.append(RecLine(*row))
            aliens.vr.discard(row[-1].v)
            aliens._cv.discard(row[0].cvv)
            aliens._cv.discard(row[0].cv)

        # complete vcv part

        # complete cv head part
        _cv_dq = deque(sorted(list(aliens._cv)))
        row: List[CVV] = []
        while _cv_dq:
            for i in range(1 + length // 2):
                if not _cv_dq:
                    break
                row.append(self.find_cvv(cvv=_cv_dq.popleft()))
                aliens.vr.discard(row[-1].v)
                row.append(self.emptyCVV)
            if row[-1] == self.emptyCVV:
                row.pop()
            self.reclist.append(RecLine(*row))
            row: List[CVV] = []
        aliens._cv.clear()

        # complete ending v part
        vr_dq = deque(sorted(list(aliens.vr)))
        row: List[CVV] = []
        while vr_dq:
            for i in range(1 + length // 2):
                if not vr_dq:
                    break
                row.append(self.find_cvv(v=vr_dq.popleft()))
                row.append(self.emptyCVV)
            if row[-1] == self.emptyCVV:
                row.pop()
            self.reclist.append(RecLine(*row))
            row: List[CVV] = []
        aliens.vr.clear()

    def save_reclist(self, reclist_dir: str) -> None:
        with open(reclist_dir, mode="w", encoding="utf-8") as reclist_file:
            reclist_str = "\n".join(str(row) for row in self.reclist)
            reclist_file.write(reclist_str)

    def save_oto(self, oto_dir: str) -> None:
        with open(oto_dir, mode="w", encoding="utf-8") as oto_file:
            oto_str = "\n".join(str(oto) for oto in self.oto)
            oto_file.write(oto_str)
            
    def check_integrity(self, aliens: Aliens) -> None:
        # _c_log = self.check_chead_integrity()
        _cv_log = self.check_cvhead_integrity(aliens._cv)
        cv_log = self.check_cv_integrity()
        vc_log = self.check_vc_integrity()
        vr_log = self.check_vr_integrity()
        
    def check_cvhead_integrity(self, cv_set: Set[str]) -> str:
        for row in self.reclist:
            cv_set.discard(row[0].cvv)
            cv_set.discard(row[0].cv)
            if self.emptyCVV in row:
                for cvv in row:
                    if cvv != self.emptyCVV:
                        cv_set.discard(cvv.cvv)
                        cv_set.discard(cvv.cv)
        _cv_log = ', '.join(cv_set)
        return _cv_log
    
    def check_cv_integrity(self, cv_set: Set[str], cv_mid: Optional[Set[str]]=None) -> str:
        cv_log = ', '.join(cv_set)
        return cv_log


def main():
    generator = CVVCReclistGenerator()
    generator.read_dict("dict_files\\CHN.txt")
    aliens = generator.get_needed_aliens()
    # aliens = generator.gen_plan_b(aliens=aliens)
    generator.gen_mora_x(aliens=aliens, length=5)
    generator.save_reclist("result\\reclist.txt")


if __name__ == "__main__":
    main()
