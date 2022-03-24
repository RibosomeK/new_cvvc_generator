from collections import namedtuple, UserList, Counter
import configparser
from dataclasses import dataclass, field
from enum import Enum
from random import choice
import re
from typing import Optional, Iterable
from .errors import *


class Cvv(namedtuple("Cvv", "cvv c v act_c fol_v cv mid_v end_v")):
    """
    take [gwaang] for example:
        cvv: gwaang
        c: k
        v: aang
        acl_c: khw (actual consonant)
        fol_v: waang (for VocalSharp)
        cv: gwA (does not include end_v)
        mid_v: aang (stretch part in lengthening a note)
        end_v: ng (the ended part)
    last three params are optional (None),
    """

    __slot__ = ()

    @staticmethod
    def new(components: Optional[Iterable[str]] = None) -> "Cvv":
        length = 8
        if components is None:
            return Cvv(*[None] * length)
        else:
            param = []
            for idx, value in enumerate(components):
                if idx > length:
                    raise WrongArgumentsNumberError(
                        f"More than {length} arguments are given."
                    )
                if value == "":
                    value = None
                param.append(value)
            param.extend([None] * (length - len(param)))
            return Cvv(*param)

    def get_cv(self, is_full_cv: Optional[bool] = False) -> str:
        """return full cv or simplified cv

        Args:
            is_full_cv (Optional[bool], optional): Defaults to False.
            By default we use simplified cv if there is one, 
            or set parameter is_full_cv to True.

        Returns:
            str: cv
        """
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
        str_order = (
            self.cvv,
            self.cv,
            self.c,
            self.v,
            self.act_c,
            self.fol_v,
            self.mid_v,
            self.end_v,
        )
        for value in str_order:
            if value:
                return str(value)
        else:
            return "R"

    def __bool__(self) -> bool:
        for ele in self:
            if ele:
                return True
        else:
            return False


class AliasType(Enum):
    C = "C"
    CV = "CV"
    VC = "VC"
    VCV = "VCV"
    V = "VR"


class VcSet(set[tuple[str, str]]):
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
            raise PopError

    def __sub__(self, __iterable: Iterable[tuple[str, str]]) -> "VcSet":
        for value in __iterable:
            self.discard(value)
        return self

    def __or__(self, __iterable: Iterable[tuple[str, str]]) -> "VcSet":
        for value in __iterable:
            self.add(value)
        return self

    def copy(self) -> "VcSet":
        new_vc_set = VcSet()
        new_vc_set.update(self)
        return new_vc_set


class AliasUnion:
    def __init__(self) -> None:
        self.__data = {
            "c_head": set(),
            "cv_head": set(),
            "cv": set(),
            "vc": VcSet(),
            "vr": set(),
            "vcv": VcSet(),
            "cv_mid": set(),
        }

        self.is_full_cv: bool = True

    @property
    def c_head(self) -> set[str]:
        return self.__data["c_head"]

    @c_head.setter
    def c_head(self, value: set[str]):
        self.__data["c_head"] = value

    @property
    def cv_head(self) -> set[str]:
        return self.__data["cv_head"]

    @cv_head.setter
    def cv_head(self, value: set[str]):
        self.__data["cv_head"] = value

    @property
    def cv(self) -> set[str]:
        return self.__data["cv"]

    @cv.setter
    def cv(self, value: set[str]):
        self.__data["cv"] = value

    @property
    def vc(self) -> VcSet:
        return self.__data["vc"]

    @vc.setter
    def vc(self, value: VcSet):
        self.__data["vc"] = value

    @property
    def vr(self) -> set[str]:
        return self.__data["vr"]

    @vr.setter
    def vr(self, value: set):
        self.__data["vr"] = value

    @property
    def vcv(self) -> VcSet:
        return self.__data["vcv"]

    @vcv.setter
    def vcv(self, value: VcSet):
        self.__data["vcv"] = value

    @property
    def cv_mid(self) -> set[str]:
        return self.__data["cv_mid"]

    @cv_mid.setter
    def cv_mid(self, value: set[str]):
        self.__data["cv_mid"] = value

    def __len__(self) -> int:
        return len(self.__data)

    def __getitem__(self, key: str) -> set:
        return self.__data[key]

    def __iter__(self):
        for value in self.__data.values():
            yield value

    def __bool__(self) -> bool:
        for value in self:
            if value:
                return True
        else:
            return False

    def copy(self) -> "AliasUnion":
        new_copy = AliasUnion()

        new_copy.update(self)
        new_copy.is_full_cv = self.is_full_cv

        return new_copy

    def update(self, other: "AliasUnion") -> None:
        for key, value in other.__data.items():
            self.__data[key].update(value)

    def difference_update(self, other: "AliasUnion") -> None:
        for key, value in other.__data.items():
            self.__data[key].difference_update(value)

    def __repr__(self) -> str:
        return ", ".join(f"{key}={value}" for key, value in self.__dict__.items())


class RecLine(tuple[Cvv, ...]):
    def __new__(cls, *args):
        recline = (x for x in args)
        return super().__new__(cls, recline)

    def __str__(self, split_symbol: str = "_") -> str:
        if isinstance(self[0], Cvv):
            if re.match("[\u30a0-\u30ff\u3040-\u309f]+", self[0].get_cv()):
                line: str = split_symbol + "".join(str(e) for e in self)
            else:
                line: str = split_symbol + split_symbol.join(str(e) for e in self)
        else:
            line: str = split_symbol.join(str(e) for e in self)

        # replace R and japanease characters
        sub_str = f"{split_symbol}R{split_symbol}"
        sub_line = re.sub("[\u30a0-\u30ff\u3040-\u309f]", "", line)
        sub_line = re.sub(f"{sub_str}", "", sub_line)

        if not sub_line.islower():
            return f"{line}_UpperCase"
        return line


class Reclist(UserList[RecLine]):
    """a list of recline"""

    def __str__(self) -> str:
        line_str = []
        for line in self:
            line_str.append(str(line))
        return "\n".join(line_str)


class Oto(namedtuple("OTO", "wav prefix alias suffix l con r pre ovl")):
    """single line of oto"""

    __slot__ = ()

    def __str__(self) -> str:
        alias = self.alias
        if self.prefix:
            alias = self.prefix + self.alias
        if self.suffix:
            alias += self.suffix
        return "{}={},{:.1f},{:.1f},{:.1f},{:.1f},{:.1f}".format(
            self.wav, alias, *self[-5:]
        )


class OtoUnion(dict[AliasType, list[Oto]]):
    """a set of otos"""

    __is_frozen = False

    @property
    def _is_frozen(self) -> bool:
        return self.__is_frozen

    @_is_frozen.setter
    def _is_freeze(self, value) -> None:
        self.__is_frozen = value

    def __init__(self):
        self[AliasType.C] = []
        self[AliasType.CV] = []
        self[AliasType.VC] = []
        self[AliasType.VCV] = []
        self[AliasType.V] = []
        self.__is_frozen = True

    def __setitem__(self, key: ..., item: ...) -> None:
        if self.__is_frozen and key not in self:
            raise ValueError("can't add new keys")
        return super().__setitem__(key, item)

    def __str__(self) -> str:
        oto_str = []
        for section in self.values():
            for oto in section:
                oto_str.append(str(oto))
        return "\n".join(oto_str)

    def __len__(self) -> int:
        length = 0
        for section in self.values():
            length += len(section)
        return length


class Vsdxmf(namedtuple("VS_OTO", "phoneme wav l pre con r ovl")):
    __slot__ = ()

    def __str__(self) -> str:
        if self.l == self.pre == self.con == self.r == self.ovl == 0:
            return ",".join(str(ele) for ele in self)
        else:
            return "{},{},{:.1f},{:.1f},{:.1f},{:.1f},{:.1f}".format(*self)

    @staticmethod
    def get_redirect(phoneme: str, redirect_phoneme: str) -> "Vsdxmf":
        return Vsdxmf(phoneme, f"#{redirect_phoneme}", 0, 0, 0, 0, 0)


class VsdxmfUnion(dict[AliasType, list[Vsdxmf]]):
    """a set of vsdxmfs"""

    __is_frozen: bool = False

    @property
    def _is_frozen(self) -> bool:
        return self.__is_frozen

    @_is_frozen.setter
    def _is_freeze(self, value) -> None:
        self.__is_frozen = value

    def __init__(self) -> None:
        self[AliasType.C] = []
        self[AliasType.CV] = []
        self[AliasType.VC] = []
        self[AliasType.VCV] = []
        self[AliasType.V] = []
        self.__is_frozen = True

    def __setitem__(self, key: ..., item: ...) -> None:
        if self.__is_frozen and key not in self:
            raise ValueError("can't add new keys")
        return super().__setitem__(key, item)

    def __str__(self) -> str:
        vsdxmf_str = []
        for section in self.values():
            for vsdxmf in section:
                vsdxmf_str.append(str(vsdxmf))
        return "\n".join(vsdxmf_str)

    def __len__(self) -> int:
        length = 0
        for section in self.values():
            length += len(section)
        return length


@dataclass
class CvvWorkshop:
    """cvv workshop that store dict information and tool"""

    cvv_set: set[Cvv] = field(default_factory=set)
    cvv_dict: dict[str, Cvv] = field(default_factory=dict)
    cv_dict: dict[str, list[Cvv]] = field(default_factory=dict)
    c_dict: dict[str, list[Cvv]] = field(default_factory=dict)
    v_dict: dict[str, list[Cvv]] = field(default_factory=dict)
    redirect_consonant_dict: dict[str, list[str]] = field(default_factory=dict)
    redirect_vowel_dict: dict[str, list[str]] = field(default_factory=dict)

    def read_dict(self, dict_dir: str) -> None:
        """read a cvvc dict in the following format:
            bao,p,ao
            pao,ph,ao
            ...
            guang,k,uang
            kuang,kh,uang
        split symbol \t can also be used
        the format can be also extend for more detail structure of the word,
        more specific can be seen in Oto class

        Args:
            dict_dir (str): the path of dict file

        Raises:
            SyntaxError: more than 8 elements are given

        [Todo]:
            comment support, both multipul lines and single
        """
        with open(dict_dir, mode="r", encoding="utf-8") as dict_file:
            dict_content = dict_file.read()

        for line in dict_content.splitlines():
            if line := line.strip():
                # also support full-width comma, semicolon for chinese user
                word = Cvv.new(re.split(r" *[,;\t ，；] *", line))
                cvv, c, v, *_ = word
                self.cvv_set.add(word)
                self.cvv_dict.setdefault(cvv, word)
                if word.cv:
                    self.cv_dict.setdefault(word.cv, []).append(word)
                self.c_dict.setdefault(c, []).append(word)
                self.v_dict.setdefault(v, []).append(word)

                """lsd_c, lsd_v = str(word.get_lsd_c), str(word.get_lsd_v)
                self.c_dict.setdefault(lsd_c, []).append(word)
                self.v_dict.setdefault(lsd_v, []).append(word)"""

    def read_presamp(self, presamp_dir: str) -> None:
        """read presamp.ini file, do not support simplified format.
        simplified means word A does not shows up in CONSONANT section or neither.

        Args:
            presamp_dir (str): presamp.ini file path
        """
        presamp_config = configparser.ConfigParser(allow_no_value=True)
        presamp_config.read(presamp_dir, encoding="utf-8")

        cv_dict: dict[str, list[str]] = {}

        for vowel, line in presamp_config["VOWEL"].items():
            cv_list = [cv for cv in line.split("=")[1].split(",")]
            for cv in cv_list:
                cv_dict.setdefault(cv, []).append(vowel)

        for consonant, line in presamp_config["CONSONANT"].items():
            cv_list = [cv for cv in line.split("=")[0].split(",")]
            for cv in cv_list:
                try:
                    cv_dict[cv].append(consonant)
                except AttributeError:
                    raise MissingCvInPresampError(
                        f"{cv} does not show up in [CONSONANT] section, please check again."
                    )

        for cv, component in cv_dict.items():
            if len(component) > 2:
                raise MultiCvInPresampError(
                    f"{cv} seems to appeared in [VOWEL] section or [CONSONANT] section multipul times."
                )
            elif len(component) == 1:
                v = c = component[0]
            else:
                v, c = component
            cvv = Cvv.new((cv, c, v))
            self.cvv_set.add(cvv)
            self.cvv_dict.setdefault(cv, cvv)
            self.c_dict.setdefault(c, []).append(cvv)
            self.v_dict.setdefault(v, []).append(cvv)

    def read_lsd(self, lsd_dir: str) -> None:
        """read .lsd file, does not support comment at this moment. does not support multi syllable.

        Args:
            lsd_dir (str): .lsd file path
        """
        with open(lsd_dir, mode="r", encoding="utf-8") as f:
            same_c_and_v_check: set = set()
            cv, c, v = "000"
            idx = 0
            for line in f.read().split("\n"):
                if re.match(r"\s*", line) is None:
                    continue
                if idx % 2 == 0:
                    cv = line
                else:
                    c, v = line.split("#")
                    if c == "":
                        c = v
                    if (c, v) in same_c_and_v_check:
                        continue
                    same_c_and_v_check.add((c, v))
                    cvv = Cvv.new((cv, c, v, c, v))
                    self.cvv_set.add(cvv)
                    self.cvv_dict.setdefault(cv, cvv)
                    self.c_dict.setdefault(c, []).append(cvv)
                    self.v_dict.setdefault(v, []).append(cvv)
                idx += 1

    def find_cvv(
        self,
        cvv: Optional[str] = None,
        c: Optional[str] = None,
        v: Optional[str] = None,
        exception: Optional[set[str]] = None,
    ) -> Cvv:
        """find a cvv class by a cvv, c, or v

        Args:
            cvv (str, optional): _description_. Defaults to None.
            c (str, optional): _description_. Defaults to None.
            v (str, optional): _description_. Defaults to None.
            exception (Optional[set[str]], optional): _description_. Defaults to None.

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            SyntaxError: _description_

        Returns: Cvv
        """
        if cvv:
            if cv := self.cvv_dict.get(cvv):
                return cv
            else:
                if cv_list := self.cv_dict.get(cvv):
                    return choice(cv_list)
                else:
                    raise CantFindCvvError(f"no cvv has a {cv} attribute")
        if c and not v:
            if cvv_list := self.c_dict.get(c):
                if exception:
                    new_cvv_list: list[Cvv] = []
                    for cv in cvv_list:
                        if cv.v not in exception:
                            new_cvv_list.append(cv)
                    cvv_list = new_cvv_list
                if not cvv_list:
                    raise CantFindCvvError(f"no cvv has consonant of {c}")
                return choice(cvv_list)
        if v and not c:
            if cvv_list := self.v_dict.get(v):
                if exception:
                    new_cvv_list: list[Cvv] = []
                    for cv in cvv_list:
                        if cv.c not in exception:
                            new_cvv_list.append(cv)
                    cvv_list = new_cvv_list
                if not cvv_list:
                    raise CantFindCvvError(f"no cvv has vowel {v}")
                return choice(cvv_list)
        if c and v:
            if cvv_list := self.c_dict.get(c):
                for cv in cvv_list:
                    if cv.v == v:
                        return cv
                else:
                    raise CantFindCvvError(f"no cvv has {c} and {v} at the same time")
        raise ArgumentTypeError("invalid arguments are given")

    def find_next(self, vc: tuple[str, str], vc_max_v: str) -> Cvv:
        try:
            return self.find_cvv(c=vc[1], v=vc_max_v)
        except CantFindCvvError:
            raise CantFindNextCvvError

    def read_redirect_config(self, redirect_config_dir) -> None:
        redirect_config = configparser.ConfigParser(allow_no_value=True)
        redirect_config.read(redirect_config_dir, encoding="utf-8")
        self.redirect_vowel_dict = {
            key: values.split(",") for key, values in redirect_config["VOWEL"].items()
        }
        self.redirect_consonant_dict = {
            key: values.split(",")
            for key, values in redirect_config["CONSONANT"].items()
        }

    def get_redirect_phoneme(
        self, phoneme: str | tuple[str, str], alias_type: AliasType
    ) -> list[str]:
        redirect_phoneme: list[str] = []
        if alias_type == AliasType.C:
            return redirect_phoneme

        elif alias_type == AliasType.CV:

            if phoneme in self.cv_dict:
                for cvv in self.cv_dict.get(str(phoneme), []):
                    _, c, v = cvv.get_lsd_cvv()
                    redirect_phoneme.append(f"{c} {v}")

        elif alias_type == AliasType.VC:
            v, c = phoneme
            if c in self.v_dict:
                redirect_consonant_dict = self.redirect_vowel_dict
            else:
                redirect_consonant_dict = self.redirect_consonant_dict

            if v in self.redirect_vowel_dict:
                for redirect_vowel in self.redirect_vowel_dict[v]:
                    redirect_phoneme.append(f"{redirect_vowel} {c}")

            if c in redirect_consonant_dict:
                for redirect_consonant in redirect_consonant_dict[c]:
                    redirect_phoneme.append(f"{v} {redirect_consonant}")

            if v in self.redirect_vowel_dict and c in redirect_consonant_dict:
                for redirect_vowel in self.redirect_vowel_dict[v]:
                    for redirect_consonant in redirect_consonant_dict[c]:
                        redirect_phoneme.append(
                            f"{redirect_vowel} {redirect_consonant}"
                        )

        elif alias_type == AliasType.V:
            for redirect_vowel in self.redirect_vowel_dict.get(str(phoneme), []):
                redirect_phoneme.append(f"{redirect_vowel} ")

        else:
            raise ArgumentTypeError("type of given alias is wrong")

        return redirect_phoneme

    def get_presamp_str(self) -> str:
        presamp_ini: list[str] = ["[VERSION]\n" "1.7"]
        presamp_ini.append("[VOWEL]")
        for v, cvv_list in self.v_dict.items():
            v_str = ",".join(str(cvv) for cvv in cvv_list)
            v_str = f"{v}={v}={v_str}=100"
            presamp_ini.append(v_str)
        presamp_ini.append("[CONSONANT]")
        for c, cvv_list in self.c_dict.items():
            if c in self.v_dict:
                continue
            c_str = ",".join(str(cvv) for cvv in cvv_list)
            c_str = f"{c}={c_str}=1"
            presamp_ini.append(c_str)
        presamp_ini.append("[ENDTYPE]\n" "%v% R\n" "[ENDFLAG]\n" "1")
        return "\n".join(presamp_ini)

    def save_presamp(self, presamp_dir: str) -> None:
        with open(presamp_dir, mode="w", encoding="utf-8") as f:
            f.write(self.get_presamp_str())

    def get_lsd_str(self) -> str:
        lsd_str = []
        for cvv in sorted(self.cvv_set, key=Cvv.get_lsd_c):
            cv, c, v = cvv.get_lsd_cvv()
            if c == v:
                lsd_str.append(f"{cv}\n#{v}")
            else:
                lsd_str.append(f"{cv}\n{c}#{v}")
        return "\n".join(lsd_str)

    def save_lsd(self, lsd_dir: str) -> None:
        with open(lsd_dir, mode="w", encoding="utf-8") as f:
            f.write(self.get_lsd_str())
