from collections import namedtuple, deque
from random import choice
from enum import Enum
from typing import List, Set, Dict, NamedTuple, Optional, Iterable
from dataclasses import dataclass, field
import configparser


Aliens_Type = Enum('Aliens_Type', 'C CV VC VCV VR')


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
    
    def get_cv(self, full_cv: Optional[bool] = False) -> str:
        if full_cv:
            return self.cvv
        else:
            return self.cv if self.cv else self.cvv

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


class OTO(namedtuple("OTO", "wav prefix alien suffix l con r pre ovl")):
    __slot__ = ()

    def __str__(self) -> str:
        alien = self.alien
        if self.prefix:
            alien = self.prefix + self.alien
        if self.suffix:
            alien += self.suffix
        return "{}={},{},{},{},{},{}".format(self.wav, alien, *self[-5:])
    

class VS_OTO(namedtuple("VS_OTO", "alien wav l pre con r ovl")):
    __slot__ = ()
    
    def __str__(self) -> str:
        return ','.join(self)


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
    
    def __or__(self, __iterable: Iterable[tuple[str, str]]) -> "VC_Set":
        for value in __iterable:
            self.add(value)
        return self


@dataclass
class Aliens:
    _c: Set[str] = field(default_factory=set)
    _cv: Set[str] = field(default_factory=set)
    cv: Set[str] = field(default_factory=set)
    vc: VC_Set = field(default_factory=VC_Set)
    vr: Set[str] = field(default_factory=set)
    vcv: VC_Set = field(default_factory=VC_Set)

    '''def __post_init__(self) -> None:
        self._c = set()
        self._cv = set()
        self.cv = set()
        self.vc = VC_Set()
        self.vr = set()
        self.vcv = VC_Set()'''

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
            self.__dict__[key].__or__(value)

    def discard(self, other: "Aliens") -> None:
        for key, value in other.__dict__.items():
            self.__dict__[key].__sub__(value)


class CVVCReclistGenerator:
    def __init__(self) -> None:
        self.cvv: Set[CVV] = set()
        self.cvv_dict: Dict[str, CVV] = {}
        self.cv_dict: Dict[str, List[CVV]] = {}
        self.c_dict: Dict[str, List[CVV]] = {}
        self.v_dict: Dict[str, List[CVV]] = {}

        self.reclist: List[RecLine] = []
        self.oto: List[NamedTuple] = []

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
                if word.cv:
                    self.cv_dict.setdefault(word.cv, []).append(word)
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
                if cv_list := self.cv_dict.get(cvv):
                    return choice(cv_list)
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
        full_cv: bool = False,
        aliens_config: Optional[str] = None,
    ) -> Aliens:
        """Get needed aliens.

        Args:
            _c (bool, optional): Begining consonant for vocalsharp. Defaults to False.
            _cv (bool, optional): Begining cv head. Defaults to True.
            full_cv (bool, optional): For cv and cv head. 
                If your dict inclued extra cv part and you WANT TO use them in non vcv part,
                you must set to False. Defaults to False.
            aliens_config (Optional[str], optional): exceptional aliens config. Defaults to None.

        Returns:
            Aliens
        """
        aliens = Aliens()
        if _c:
            aliens._c = {x for x in self.c_dict.keys()}
        aliens.cv = {cv.get_cv(full_cv) for cv in self.cvv}
        if _cv:
            aliens._cv = aliens.cv.copy()
        aliens.vc = VC_Set()
        aliens.vc.update(
            (v, c) 
            for v in self.v_dict.keys()
            for c in self.c_dict.keys()
        )
        aliens.vr = {v for v in self.v_dict.keys()}
        if aliens_config:
            unneeded, needed = self.read_aliens_config(aliens_config)
            aliens.add(needed)
            aliens.discard(unneeded)
        if aliens.vcv:
            aliens.vcv = aliens.vcv - aliens.vc
        self.aliens = aliens
        return aliens

    def read_aliens_config(self, aliens_config: str, full_cv: bool = False) -> tuple[Aliens, Aliens]:
        """Read aliens config to get unwanted aliens and wanted aliens.
        For config format plz check on the comments in config

        Args:
            aliens_config (str): config path.
            full_cv (bool): For cv and cv head. Details in self.get_needed_aliens()

        Raises:
            ValueError: Given a wrong value like there is no 'R' but get one. 

        Returns:
            tuple[unneeded_Aliens, needed_Aliens]
        """
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
                            cvv.get_cv(full_cv) for cvv in self.c_dict[cv]
                        )
                    else:
                        raise ValueError
            elif key == "vc":
                for vc in value.split(","):
                    if vc in self.c_dict:
                        unneeded.vc.update((v, vc) for v in self.v_dict)
                    if vc in self.v_dict:
                        unneeded.vc.update((vc, c) for c in self.c_dict)
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
                            (v, cvv.get_cv())
                            for v in self.v_dict.keys()
                            for cvv in self.c_dict[vcv]
                        )
                    elif vcv in self.v_dict.keys():
                        unneeded.vcv.update(
                            (vcv, cvv.get_cv()) 
                            for cvv in self.cvv
                        )
                    elif " " in vcv:
                        unneeded.vcv.add(tuple(vcv.split(" ")))
        vcv_value = config["NEEDED"]["vcv"]
        if vcv_value.upper() == "ALL":
            needed.vcv.update(
                (v, cvv.get_cv()) 
                for v in self.v_dict
                for cvv in self.cvv
            )
        elif "," in vcv_value:
            for vcv in vcv_value.split(","):
                if vcv in self.c_dict.keys():
                    needed.vcv.update(
                        (v, cvv.get_cv())
                        for v in self.v_dict.keys()
                        for cvv in self.c_dict[vcv]
                    )
                elif vcv in self.v_dict.keys():
                    needed.vcv.update(
                        (vcv, cvv.get_cv()) 
                        for cvv in self.cvv
                    )
                elif " " in vcv:
                    needed.vcv.add(tuple(vcv.split(" ")))
        return unneeded, needed

    def gen_2mora(self, aliens: Aliens) -> None:
        cv_list = list(aliens.cv | aliens._cv)
        cv_list.sort()
        for cv in cv_list:
            cvv = self.find_cvv(cvv=cv)
            if cvv:
                self.reclist.append(RecLine(cvv, cvv))
                aliens.vc.discard((cvv.v, cvv.c))
                if aliens.vcv:
                    aliens.vcv.discard((cvv.v, cvv.get_cv()))
                aliens.vr.discard(cvv.v)
            else:
                print(f"{cv}= has no match word.")
                raise ValueError
        if aliens.vcv:
            vcv_list = list(aliens.vcv)
            vcv_list.sort()
            for vcv in vcv_list:
                v = CVV(*[None]*7)
                v._replace(v=vcv[0])
                cvv = self.find_cvv(cvv=vcv[1])
                self.reclist.append(RecLine((v, cvv)))
                aliens.vc.discard((v.v, cvv.c))
                aliens.vr.discard(cvv.v)
        vc_list = list(aliens.vc)
        vc_list.sort()
        for vc in vc_list:
            v, c = CVV(*[None]*7), CVV(*[None]*7)
            v._replace(v=vc[0]), c._replace(c=vc[1])
            self.reclist.append(RecLine((v, c)))
        if vr_deque := deque(sorted(list(aliens.vr))):
            row: List[CVV] = []
            while vr_deque:
                vr = vr_deque.popleft()
                vr = CVV(None, None, vr, None, None, None, None)
                if len(row) < 3:
                    row.extend([vr, self.emptyCVV])
                else:
                    self.reclist.append(RecLine(*row))
                    row.clear()
            if row:
                self.reclist.append(RecLine(*row))

    def gen_plan_b(self, aliens: Aliens) -> Aliens:
        all_cv = list(aliens.cv | aliens._cv)
        all_cv.sort()
        for cv in all_cv:
            if cv := self.find_cvv(cv):
                self.reclist.append(RecLine(cv, cv, cv))
                aliens.vc.discard((cv.v, cv.c))
                aliens.vr.discard(cv.v)
                if aliens.vcv:
                    aliens.vcv.discard((cv.v, cv.get_cv()))
            else:
                raise ValueError
        aliens.cv.clear()
        aliens._cv.clear()
        return aliens

    def gen_mora_x(
        self, 
        aliens: Aliens, 
        length: int, 
        cv_mid: Optional[Set[str]] = None
    ) -> None:
        """Generate given x length long pre row of reclist.

        Args:
            aliens (Aliens): Needed aliens
            length (int): length pre row
            cv_mid (Optional[Set[str]], optional): 
                For some consonant is shorter in the beginning 
                that can be hard to oto like [y], [w] in manderin. 
                Defaults to None.

        Returns: None
        """
        cv_mid = cv_mid if cv_mid else set()

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
                    aliens.vc.discard((row[i-1].v, cv.c))
                    aliens.vcv.discard((row[i-1].v, cv.get_cv()))
                else:
                    aliens.vr.discard(cv.v)
            self.reclist.append(RecLine(*row))
        aliens.cv.clear()
        
        # complete vcv part
        row: List[CVV] = []
        i = 0
        while True:
            if not aliens.vcv:
                break
            if i == 0:
                vcv = aliens.vcv.pop(v=aliens.vcv.max_v[0])
                v_cvv = self.find_cvv(v=vcv[0])
                cv_cvv = self.find_cvv(cvv=vcv[1])
                aliens.vc.discard((v_cvv.v, cv_cvv.c))
                row = [v_cvv, cv_cvv]
                i += 2
            elif i <= length - 1:
                try:
                    vcv = aliens.vcv.pop(v=row[-1].v)
                    next_cv = self.find_cvv(cvv=vcv[1])
                    aliens.vc.discard((vcv[0], next_cv.c))
                    row.append(next_cv)
                    i += 1
                except ValueError:
                    if i <= length - 2:
                        vcv = aliens.vcv.pop()
                        cv1 = self.find_cvv(v=vcv[0])
                        cv2 = self.find_cvv(cvv=vcv[1])
                        aliens.vc.discard((row[-1].v, cv1.c))
                        aliens.vc.discard((cv1.v, cv2.c))
                        row.extend([cv1, cv2])
                        i += 2
                    else:
                        i = length
                        continue
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
                        row.extend([cv1, cv2])
                        i += 2
                    else:
                        i = length
                        continue
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
        
    def gen_oto(self, aliens: Aliens, bpm: float, full_cv: bool = False, cv_mid: Set[str]=None):
        """Generate all otos.

        Args:
            aliens (Aliens): [description]
        """
        cv_mid = cv_mid if cv_mid else set()
        cv_oto_list: List[OTO] = []
        vc_oto_list: List[OTO] = []
        vcv_oto_list: List[OTO] = []
        vr_oto_list: List[OTO] = []
        for row in self.reclist:
            wav = str(row)
            if row[0] == row[1] == row[2]:
                if (_cv := row[0].get_cv(full_cv)) in aliens._cv:
                    _cv_alien = f'- {row[0].get_cv(full_cv)}'
                    _cv_oto = self.get_oto(Aliens_Type.CV, wav, _cv_alien, 0, bpm)
                    cv_oto_list.append(_cv_oto)
                    aliens._cv.discard(_cv)
                if (cv := row[1].get_cv(full_cv)) in aliens.cv:
                    cv_alien = row[1].get_cv(full_cv)
                    cv_L_alien = f'{row[2].get_cv(full_cv)}_L'
                    cv_oto = self.get_oto(Aliens_Type.CV, wav, cv_alien, 1, bpm)
                    cv_L_oto = self.get_oto(Aliens_Type.CV, wav, cv_L_alien, 2, bpm)
                    cv_oto_list.extend((cv_oto, cv_L_oto))
                    aliens.cv.discard(cv)
                if (vc := (row[0].v, row[1].c)) in aliens.vc:
                    vc_oto = self.get_oto(Aliens_Type.VC, wav, vc, 1, bpm)
                    vc_oto_list.append(vc_oto)
                    aliens.vc.discard(vc)
                if (vcv := (row[0].v, row[1].get_cv())) in aliens.vcv:
                    vcv_oto = self.get_oto(Aliens_Type.VCV, wav, vcv, 1, bpm)
                    vcv_oto_list.append(vcv_oto)
                    aliens.vcv.discard(vcv)
                if (vr := row[2]) in aliens.vr:
                    vr_alien = f'{row[2].v} R'
                    vr_oto = self.get_oto(Aliens_Type.VR, wav, vr_alien, 2, bpm)
                    vr_oto_list.append(vr_oto)
                    aliens.vr.discard(vr)
            else:
                for idx, cvv in enumerate(row):
                    if idx == 0:
                        cv = cvv.get_cv(full_cv)
                        if cv in aliens._cv:
                            _cv_alien = f'- {cv}'
                            oto = self.get_oto(Aliens_Type.CV, wav, _cv_alien, idx, bpm)
                            cv_oto_list.append(oto)
                            aliens._cv.discard(cv)
                        if cv in aliens.cv and cv not in cv_mid:
                            oto = self.get_oto(Aliens_Type.CV, wav, cv, idx, bpm)
                            cv_oto_list.append(oto)
                            aliens._cv.discard(cv)
                    elif idx <= len(row)-1:
                        if (cv := cvv.get_cv(full_cv)) in aliens.cv:
                            oto = self.get_oto(Aliens_Type.CV, wav, cv, idx, bpm)
                            cv_oto_list.append(oto)
                            aliens._cv.discard(cv)
                        if (vc := (row[idx-1].v, cvv.c)) in aliens.vc:
                            oto = self.get_oto(Aliens_Type.VC, wav, vc, idx, bpm)
                            vc_oto_list.append(oto)
                            aliens.vc.discard(vc)
                        if (vcv := (row[idx-1].v, cvv.get_cv())) in aliens.vcv:
                            oto = self.get_oto(Aliens_Type.VCV, wav, vcv, idx, bpm)
                            vcv_oto_list.append(oto)
                            aliens.vcv.discard(vcv)
                    if idx == len(row)-1 and (vr := row[idx].v) in aliens.vr:
                        vr_alien = f'{vr} R'
                        oto = self.get_oto(Aliens_Type.VR, wav, vr_alien, idx, bpm)
                        vr_oto_list.append(oto)
                        aliens.vr.discard(vr)
        self.oto.extend(cv_oto_list)
        self.oto.extend(vc_oto_list)
        self.oto.extend(vcv_oto_list)
        self.oto.extend(vr_oto_list)
                        
    def gen_vsdxmf(
        self, 
        aliens: Aliens, 
        bpm: float, 
        full_cv: bool = False, 
        cv_mid: Set[str]=None, 
        redirect_config_dir: Optional[str]=None
    ) -> None:
        """Generate vsdxmf for vocalsharp.

        Args:
            aliens (Aliens): [description]
            bpm (float): [description]
            full_cv (bool, optional): [description]. Defaults to False.
            cv_mid (Set[str], optional): [description]. Defaults to None.
            redirect_config_dir (Optional[str], optional): [description]. Defaults to None.
        """
        cv_mid = cv_mid if cv_mid else set()
        c_vsdxmf_list: List[VS_OTO] = []
        cv_vsdxmf_list: List[VS_OTO] = []
        vc_vsdxmf_list: List[VS_OTO] = []
        vr_vsdxmf_list: List[VS_OTO] = []
        
            
        
    def get_oto(
        self, 
        aliens_type: Aliens_Type, 
        wav: str,
        alien: str | tuple[str, str], 
        position: int,
        bpm: float
    ) -> OTO:
        """Get one sigle oto.

        Args:
            aliens_type (str): the type of alien: [cv, vc, vcv, vr]
            wav (str) : the string of wav
            alien (str or tuple[str, str]): alien in oto, tuple for vc and vcv types
            position (int): position in row, start from 0. for vc and vcv types use the c or cv position
            bpm (float): the bpm of recording BGM

        Returns:
            OTO the class
        """
        bpm_param = float(120 / bpm)
        beat = bpm_param*(1250 + position*500)
        OVL, CONSONANT_VEL, VOWEL_VEL = 80, 100, 200
            
        if aliens_type == Aliens_Type.CV:
            offset = beat - CONSONANT_VEL
            consonant = 0.25*500*bpm_param + CONSONANT_VEL
            cutoff = -(beat + 0.75*500*bpm_param)
            preutterance = CONSONANT_VEL
            overlap = CONSONANT_VEL / 2
        elif aliens_type == Aliens_Type.VR:
            offset = beat + 500*bpm_param - OVL - VOWEL_VEL
            consonant = OVL + VOWEL_VEL + 100
            cutoff = -(consonant + 100)
            preutterance = OVL + VOWEL_VEL
            overlap = OVL
        elif aliens_type == Aliens_Type.VC:
            alien = '{} {}'.format(*alien)
            offset = beat - OVL - VOWEL_VEL - CONSONANT_VEL
            consonant = OVL + VOWEL_VEL + 0.33*CONSONANT_VEL
            cutoff = -(OVL + VOWEL_VEL + CONSONANT_VEL)
            preutterance = OVL + VOWEL_VEL
            overlap = OVL
        elif aliens_type == Aliens_Type.VCV:
            alien = '{} {}'.format(*alien)
            offset = beat - OVL - VOWEL_VEL - CONSONANT_VEL
            consonant = OVL + VOWEL_VEL + CONSONANT_VEL + 0.25*500*bpm_param
            cutoff = -(OVL + VOWEL_VEL + CONSONANT_VEL + 0.75*500*bpm_param)
            preutterance = OVL + VOWEL_VEL + CONSONANT_VEL
            overlap = OVL
        else:
            raise TypeError
            
        oto = OTO(wav, None, alien, None, offset, consonant, cutoff, preutterance, overlap)
        return oto
    
    def get_vs_oto(
        self,
        aliens_type: Aliens_Type, 
        wav: str,
        alien: str | tuple[str, str], 
        position: int,
        bpm: float, 
        redirect_config: Optional[configparser.ConfigParser]=None
    ) -> VS_OTO:
        bpm_param = float(120 / bpm)
        beat = bpm_param*(1250 + position*500)
        OVL, CONSONANT_VEL, VOWEL_VEL = 80, 100, 200
            
        if aliens_type == Aliens_Type.C:
            phoneme = f' {alien}'
            offset = beat - 20 - CONSONANT_VEL
            preutterance = offset + 20
            consonant = preutterance + 0.25*CONSONANT_VEL
            cutoff = consonant + CONSONANT_VEL
            overlap = offset + 5
        if aliens_type == Aliens_Type.CV:
            cvv = self.find_cvv(cvv=str(alien))
            phoneme = f'{cvv.c} {cvv.v}'
            offset = beat - CONSONANT_VEL
            preutterance = beat
            consonant = 0.25*500*bpm_param + preutterance
            cutoff = consonant + 0.75*500*bpm_param
            overlap = offset + CONSONANT_VEL / 2
        elif aliens_type == Aliens_Type.VR:
            phoneme = f'{alien} '
            offset = beat + 500*bpm_param - OVL - VOWEL_VEL
            preutterance = offset + OVL + VOWEL_VEL
            consonant = preutterance + 100
            cutoff = consonant + 100
            overlap = offset + OVL
        elif aliens_type == Aliens_Type.VC:
            phoneme = '{} {}'.format(*alien)
            offset = beat - OVL - VOWEL_VEL - CONSONANT_VEL
            preutterance = beat - CONSONANT_VEL
            consonant = preutterance + 0.33*CONSONANT_VEL
            cutoff = beat
            overlap = offset + OVL
            '''
        elif aliens_type == Aliens_Type.VCV:
            alien = '{} {}'.format(*alien)
            offset = beat - OVL - VOWEL_VEL - CONSONANT_VEL
            preutterance = beat
            consonant = beat + 0.25*500*bpm_param
            cutoff = beat + 0.75*500*bpm_param
            overlap = offset + OVL
            '''
        else:
            raise TypeError
        
        old_phoneme = phoneme
        if redirect_config:
            redirect_vowel = {
                value: key 
                for key, values in redirect_config['VOWEL'] 
                for value in values.split(',')
            }
            redirect_consonant = {
                value: key
                for key, values in redirect_config['CONSONANT']
                for value in values.split(',')
            }
            if aliens_type == Aliens_Type.C:
                alien = str(alien)
                phoneme = f' {redirect_consonant.get(alien, alien)}'
            elif aliens_type == Aliens_Type.CV:
                c, v = alien
                c = redirect_consonant.get(c, c)
                v = redirect_vowel.get(v, v)
                phoneme = f'{c} {v}'
            elif aliens_type == Aliens_Type.VR:
                alien = str(alien)
                phoneme = f'{redirect_vowel.get(alien, alien)} '
            elif aliens_type == Aliens_Type.VC:
                v, c = alien
                v = redirect_vowel.get(v, v)
                c = redirect_consonant.get(c, c)
                phoneme = f'{v} {c}'
            else:
                raise TypeError
        
        if old_phoneme != phoneme:
            wav = f'#{old_phoneme}'
            offset, preutterance, consonant, cutoff, overlap = 0, 0, 0, 0, 0
        
        vs_oto = VS_OTO(phoneme, wav, offset, preutterance, consonant, cutoff, overlap)
        return vs_oto

    def save_reclist(self, reclist_dir: str) -> None:
        with open(reclist_dir, mode="w", encoding="utf-8") as reclist_file:
            reclist_str = "\n".join(str(row) for row in self.reclist)
            reclist_file.write(reclist_str)

    def save_oto(self, oto_dir: str) -> None:
        with open(oto_dir, mode="w", encoding="utf-8") as oto_file:
            oto_str = "\n".join(str(oto) for oto in self.oto)
            oto_file.write(oto_str)
            
    def save_presamp(self, presamp_dir: str) -> None:
        presamp_ini: List[str] = ['[VERSION]\n'
                                  '1.7']
        presamp_ini.append('[VOWEL]')
        for v, cvv_list in self.v_dict.items():
            v_str = ','.join(str(cvv) for cvv in cvv_list)
            v_str = f'{v}={v}={v_str}=100'
            presamp_ini.append(v_str)
        presamp_ini.append('[CONSONANT]')
        for c, cvv_list in self.c_dict.items():
            if c in self.v_dict:
                continue
            c_str = ','.join(str(cvv) for cvv in cvv_list)
            c_str = f'{c}={c_str}=1'
            presamp_ini.append(c_str)
        presamp_ini.append('[ENDTYPE]\n'
                           '%v% R\n'
                           '[ENDFLAG]\n'
                           '1')
        with open(presamp_dir, mode='w', encoding='utf-8') as f:
            f.write('\n'.join(presamp_ini))
            
    def check_integrity(self, aliens: Aliens) -> None:
        # _c_log = self.check_chead_integrity()
        _cv_log = self.check_cvhead_integrity(aliens._cv)
        cv_log = self.check_cv_integrity(aliens.cv)
        vcv_log = self.check_vcv_integrity(aliens.vcv)
        vc_log = self.check_vc_integrity(aliens.vc)
        vr_log = self.check_vr_integrity(aliens.vr)
        print(f'Missing cv head: {_cv_log}\n'
              f'Missing cv: {cv_log}\n'
              f'Missing vcv: {vcv_log}\n'
              f'Missing vc: {vc_log}\n'
              f'Missing ending v: {vr_log}')
        
    def check_cvhead_integrity(self, cv_set: Set[str]) -> str:
        for row in self.reclist:
            cv_set.discard(row[0].cvv)
            cv_set.discard(row[0].cv)
            if self.emptyCVV in row:
                for cvv in row:
                    if cvv != self.emptyCVV:
                        cv_set.discard(cvv.cvv)
                        cv_set.discard(cvv.cv)
        _cv_log = ', '.join(cv_set) if cv_set else 'None'
        return _cv_log
    
    def check_cv_integrity(self, cv_set: Set[str], cv_mid: Optional[Set[str]]=None) -> str:
        cv_mid = cv_mid if cv_mid else set()
        for row in self.reclist:
            for idx, cvv in enumerate(row):
                if idx == 0 and (cvv.cv in cv_mid or cvv.cvv in cv_mid):
                    continue
                cv_set.discard(cvv.cvv)
                cv_set.discard(cvv.cv)
        cv_log = ', '.join(cv_set) if cv_set else 'None'
        return cv_log
    
    def check_vc_integrity(self, vc_set: Set[tuple[str, str]]) -> str:
        for row in self.reclist:
            for idx, cvv in enumerate(row):
                if idx == 0:
                    continue
                vc_set.discard((row[idx-1].v, cvv.c))
        vc_log = ", ".join(str(vc) for vc in vc_set) if vc_set else 'None'
        return vc_log
    
    def check_vcv_integrity(self, vcv_set: Set[tuple[str, str]]) -> str:
        for row in self.reclist:
            for idx, cvv in enumerate(row):
                if idx == 0:
                    continue
                vcv_set.discard((row[idx-1].v, cvv.get_cv()))
        vcv_log = ", ".join(str(vcv) for vcv in vcv_set) if vcv_set else 'None'
        return vcv_log
            
    def check_vr_integrity(self, vr_set: Set[str]) -> str:
        for row in self.reclist:
            vr_set.discard(row[-1].v)
        vr_log = ', '.join(vr_set) if vr_set else 'None'
        return vr_log


def main():
    generator = CVVCReclistGenerator()
    generator.read_dict("dict_files\\CHN.txt")
    aliens = generator.get_needed_aliens(aliens_config=".\\config\\aliens_config.ini")
    aliens = generator.gen_plan_b(aliens=aliens)
    generator.gen_mora_x(aliens=aliens, length=8)
    generator.gen_oto(generator.get_needed_aliens(aliens_config=".\\config\\aliens_config.ini"), 120)
    generator.save_reclist("result\\reclist.txt")
    generator.save_oto("result\\oto.txt")
    generator.save_presamp("result\\presamp.ini")
    generator.check_integrity(generator.get_needed_aliens())

if __name__ == "__main__":
    main()
