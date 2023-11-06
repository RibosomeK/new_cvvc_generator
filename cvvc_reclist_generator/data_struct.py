from collections import UserList
import configparser
from enum import Enum
from dataclasses import dataclass, field, fields
from typing import Counter, Iterator, Optional, Iterable
from abc import ABC, abstractmethod
import re
import random

from .errors import (
    AliasTypeError,
    ArgumentTypeError,
    CantFindCvvError,
    CantFindNextCvvError,
    MissingCvInPresampError,
    MultiCvInPresampError,
    PopError,
)


class AliasType(Enum):
    C = "C"
    CV = "CV"
    VC = "VC"
    VCV = "VCV"
    V = "VR"
    C_HEAD = "C_HEAD"
    CV_HEAD = "CV_HEAD"
    CV_LONG = "CV_LONG"

    REDIRECT = "REDIRECT"


@dataclass(slots=True)
class Alias:
    _alias: tuple[str, ...]
    _type: AliasType

    def __init__(
        self, alias: str | tuple[str, ...], alias_type: AliasType | str
    ) -> None:
        if isinstance(alias, tuple):
            self._alias = alias

        elif len(splitted := alias.split(" ")) == 2:
            self._alias = (splitted[0], splitted[1])

        else:
            self._alias = (alias,)

        if isinstance(alias_type, str):
            alias_type = AliasType(alias_type)
        self._type = alias_type

    @property
    def alias(self):
        return self._alias

    @property
    def type(self):
        return self._type

    def __str__(self) -> str:
        return " ".join(self._alias)

    def __len__(self) -> int:
        return len(self._alias)

    def __getitem__(self, idx: int) -> str:
        return self._alias.__getitem__(idx)

    def __eq__(self, other: "Alias") -> bool:
        return self._alias == other.alias and self._type == other._type

    def __hash__(self) -> int:
        return hash((*self._alias, self._type))


@dataclass(slots=True)
class Cvv:
    """
    take [gwaang] for example:
        cvv: gwaang
        c: k
        v: aang
        alias_c: khw (actual consonant)
        alias_v: waang (for VocalSharp)
        cv: gwA (does not include end_v)
        mid_v: aang (stretch part in lengthening a note)
        end_v: ng (the ended part)
    last three params are optional (None),
    """

    cvv: str
    c: str
    v: str
    alias_c: str = ""
    alias_v: str = ""
    cv: str = ""
    mid_v: str = ""
    end_v: str = ""

    _STR_ORDER = "cvv cv c v alias_c alias_v mid_v end_v"
    _ITER_ORDER = "cvv c v alias_c alias_v cv mid_v end_v"

    @staticmethod
    def new(components: Optional[Iterable[str]] = None) -> "Cvv":
        length = 8
        if components is None:
            return Cvv(*[""] * length)
        else:
            param = []
            for idx, value in enumerate(components):
                if idx > length:
                    raise ValueError(f"More than {length} arguments are given.")
                param.append(value)
            param.extend([None] * (length - len(param)))
            return Cvv(*param)

    @staticmethod
    def new_with(component: tuple[AliasType, str]) -> "Cvv":
        alias_type, alias = component
        if alias_type == AliasType.C:
            return Cvv("", alias, "", "", "", "", "", "")

        if alias_type == AliasType.V:
            return Cvv("", "", alias, "", "", "", "", "")

        raise AliasTypeError("unsupported alias type in this method.")

    def get_cv(self, is_full_cv: Optional[bool] = False) -> str:
        """return full cv or simplified cv

        Args:
            is_full_cv (Optional[bool], optional): Defaults to False.
            By default we use simplified cv if there is one,
            or set parameter is_full_cv to True.

        Returns:
            str: cv
        """

        if not (self.cvv or self.cv):
            return str(self)

        if is_full_cv:
            return self.cvv
        else:
            return self.cv if self.cv else self.cvv

    def get_lsd_c(self) -> str:
        return self.alias_c if self.alias_c else self.c

    def get_lsd_v(self) -> str:
        return self.alias_v if self.alias_v else self.v

    def get_v(self, use_end_v: Optional[bool] = False) -> str:
        if use_end_v:
            return self.end_v if self.end_v else self.v
        return self.v

    def get_lsd_cvv(self) -> tuple[str, str, str]:
        cvv = self.get_cv()
        c = self.get_lsd_c()
        v = self.get_lsd_v()
        return (cvv, c, v)

    def __str__(self) -> str:
        for value in self:
            if value:
                return str(value)
        else:
            return "R"

    def __eq__(self, cvv: "Cvv") -> bool:
        for attr in self._ITER_ORDER.split(" "):
            if getattr(self, attr) != getattr(cvv, attr):
                return False
        else:
            return True

    def __iter__(self) -> Iterator[str]:
        for name in self._ITER_ORDER.split(" "):
            yield getattr(self, name)

    def __getitem__(self, idx: int) -> str:
        return getattr(self, self._ITER_ORDER.split(" ")[idx])

    def __bool__(self) -> bool:
        return any(self)

    def __hash__(self) -> int:
        return hash("".join([e for e in self if e]))


@dataclass
class Digits:
    def __str__(self) -> str:
        return ",".join(f"{digit:.1f}" for digit in self)

    def __iter__(self) -> Iterator[float]:
        for fd in fields(self):
            yield getattr(self, fd.name)


@dataclass
class UDigits(Digits):
    lft: float
    con: float
    rft: float
    pre: float
    ovl: float


@dataclass
class VDigits(Digits):
    lft: float
    pre: float
    con: float
    rft: float
    ovl: float

    def __str__(self) -> str:
        if any(self):
            return super().__str__()
        else:
            return ",".join(f"{int(digit)}" for digit in self)


class Label(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def shift(self, shift: int) -> None:
        pass


@dataclass(slots=True)
class Oto(Label):
    def __init__(
        self,
        wav: str,
        alias: tuple[str | tuple[str, str], str | AliasType] | Alias,
        digits: Iterable[float],
        prefix: str = "",
        suffix: str = "",
    ) -> None:
        self.wav: str = wav
        self.alias: Alias
        self.digits: UDigits = UDigits(*digits)
        self.prefix: str = prefix
        self.suffix: str = suffix

        if isinstance(alias, Alias):
            self.alias = alias
        else:
            self.alias = Alias(*alias)

    def __str__(self) -> str:
        alias = str(self.alias)

        if self.alias._type in (AliasType.CV_HEAD, AliasType.C_HEAD):
            alias = f"- {alias}"
        elif self.alias._type == AliasType.CV_LONG:
            alias = f"{alias}_L"
        elif self.alias._type == AliasType.V:
            alias = f"{alias} R"

        if self.prefix:
            alias = self.prefix + alias
        if self.suffix:
            alias += self.suffix
        return f"{self.wav}={alias},{self.digits}"

    def shift(self, shift: int) -> None:
        for digit in self.digits:
            digit += shift


@dataclass(slots=True)
class Vsdxmf(Label):
    def __init__(
        self,
        phoneme: tuple[str, str, AliasType] | tuple[str, AliasType],
        wav: str,
        digits: Iterable[float] | VDigits,
    ) -> None:
        self.phoneme: tuple[str, str, AliasType]
        self.wav: str = wav
        self.digits: VDigits = VDigits(*digits)

        if len(phoneme) == 3:
            self.phoneme = phoneme
        else:
            phoneme_sp = phoneme[0].split(" ")
            if phoneme[-1] == AliasType.CV_LONG:
                self.phoneme = (phoneme_sp[0], f"{phoneme_sp[1]}_L", phoneme[-1])
            elif len(phoneme_sp) == 2:
                self.phoneme = (phoneme_sp[0], phoneme_sp[1], phoneme[-1])
            elif phoneme[-1] == AliasType.C_HEAD:
                self.phoneme = ("", *phoneme)
            else:
                self.phoneme = (phoneme[0], "", phoneme[-1])

    def __str__(self) -> str:
        alias_type = self.phoneme[-1]
        phoneme_str = " ".join(self.phoneme[:-1])

        if alias_type == AliasType.CV_LONG:
            phoneme_str += "_L"
        return f"{phoneme_str},{self.wav},{self.digits}"

    @staticmethod
    def get_redirect(phoneme: str, redirect_phoneme: str) -> "Vsdxmf":
        return Vsdxmf(
            (phoneme, AliasType.REDIRECT), f"#{redirect_phoneme}", (0, 0, 0, 0, 0)
        )

    def shift(self, shift: int) -> None:
        for digit in self.digits:
            digit += shift


@dataclass(slots=True)
class Recline:
    _data: tuple[Cvv, ...]
    NONE_UNDERLINE = ("[\u30a0-\u30ff\u3040-\u309f]+", "[\u4e00-\u9fa5]+", "[0-9]")

    def __init__(self, cvv: Iterable[Cvv]) -> None:
        self._data = tuple(cvv)

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, idx: int) -> Cvv:
        return self._data[idx]

    def __iter__(self) -> Iterator[Cvv]:
        return iter(self._data)

    def __str__(self) -> str:
        temp_str = []
        is_pre_word_latin = True
        is_curr_word_latin = True
        is_upper_case = False
        for cvv in self._data:
            cvv_str = str(cvv)

            if is_pre_word_latin:
                temp_str.append("_")

            for pattern in self.NONE_UNDERLINE:
                if re.match(pattern, cvv_str) is not None:
                    is_curr_word_latin = False
                    break
            else:
                is_curr_word_latin = True

            if not is_pre_word_latin and is_curr_word_latin:
                temp_str.append("_")

            is_pre_word_latin = is_curr_word_latin

            if cvv_str == "R":
                temp_str.append(cvv_str)
                continue

            temp_str.append(cvv_str)

            if is_pre_word_latin and not cvv_str.islower():
                is_upper_case = True

        if temp_str[-1] == "R":
            temp_str = temp_str[:-2]

        if is_upper_case:
            temp_str.append("_UpperCase")

        return "".join(temp_str)


class Reclist(UserList[Recline]):
    def __str__(self) -> str:
        return "\n".join([str(recline) for recline in self])


@dataclass
class LabelUnion(ABC):
    _is_froze: bool = True

    @property
    def is_froze(self) -> bool:
        return self._is_froze

    @is_froze.setter
    def is_froze(self, is_froze: bool) -> None:
        self._is_froze = is_froze

    def __str__(self) -> str:
        return "\n".join(["\n".join(str(label) for label in self)])

    def __iter__(self) -> Iterator[Label]:
        for fd in fields(self):
            labels = getattr(self, fd.name)
            if not isinstance(labels, Iterable):
                continue
            for label in labels:
                yield label

    def __len__(self) -> int:
        length = 0
        for _ in self:
            length += 1
        return length


@dataclass(slots=True)
class OtoUnion(LabelUnion):
    C: list[Oto] = field(default_factory=list)
    CV: list[Oto] = field(default_factory=list)
    VC: list[Oto] = field(default_factory=list)
    VCV: list[Oto] = field(default_factory=list)
    V: list[Oto] = field(default_factory=list)


@dataclass(slots=True)
class VsdxmfUnion(LabelUnion):
    C: list[Vsdxmf] = field(default_factory=list)
    CV: list[Vsdxmf] = field(default_factory=list)
    VC: list[Vsdxmf] = field(default_factory=list)
    V: list[Vsdxmf] = field(default_factory=list)


@dataclass(slots=True)
class VcSet:
    """a set to store vc like components and recording max value according to v or c."""

    _data: set[Alias]
    _c_counter: Counter[str]
    _v_counter: Counter[str]

    def __init__(self, vc_likes: Optional[Iterable[Alias]] = None):
        self._data: set[Alias] = set()
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

    def update(self, vc: Iterable[Alias]) -> None:
        for alias in vc:
            self.add(alias)

    def add(self, vc: Alias) -> None:
        if len(vc) != 2:
            raise ValueError("not a vc-like alias")

        if vc not in self:
            self._data.add(vc)
            self._update_counter(vc, True)

    def discard(self, vc: Alias) -> None:
        if vc in self:
            self._data.discard(vc)
            self._update_counter(vc, False)

    def pop(self) -> Alias:
        if not self:
            raise KeyError("pop from an empty set")

        vc = self._data.pop()
        self._update_counter(vc, False)
        return vc

    def pop_by(self, v: Optional[str] = None, c: Optional[str] = None) -> Alias:
        """pop vc with given v and c"""
        for vc in self._data:
            if v and vc[0] == v:
                self.discard(vc)
                return vc

            if c and vc[1] == v:
                self.discard(vc)
                return vc

        raise PopError("not found")

    def copy(self) -> "VcSet":
        return VcSet(self._data)

    def difference_update(self, other: "VcSet") -> None:
        other = other.copy()
        while other:
            self.discard(other.pop())

    def clear(self) -> None:
        self._data.clear()
        self._v_counter.clear()
        self._c_counter.clear()

    def _update_counter(self, vc: Alias, is_add: bool) -> None:
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

    def __iter__(self) -> Iterator[Alias]:
        return iter(self._data)

    def __str__(self) -> str:
        return f"VcSet: {self._data}"

    def __contains__(self, vc: Alias) -> bool:
        return vc in self._data

    def __bool__(self) -> bool:
        return bool(self._data)


@dataclass(slots=True)
class AliasUnion:
    c_head: set[Alias] = field(default_factory=set)
    cv_head: set[Alias] = field(default_factory=set)
    c: set[Alias] = field(default_factory=set)
    cv: set[Alias] = field(default_factory=set)
    vc: VcSet = field(default_factory=VcSet)
    vcv: VcSet = field(default_factory=VcSet)
    v: set[Alias] = field(default_factory=set)

    IS_FULL_CV: bool = True
    USE_END_V: bool = False

    def update(self, other: "AliasUnion") -> None:
        for fd in fields(self):
            aliases = getattr(self, fd.name)
            if isinstance(aliases, bool):
                setattr(self, fd.name, getattr(other, fd.name))
            else:
                aliases.update(getattr(other, fd.name))

    def difference_update(self, other: "AliasUnion") -> None:
        for fd in fields(self):
            aliases = getattr(self, fd.name)
            if isinstance(aliases, bool):
                setattr(self, fd.name, getattr(other, fd.name))
            else:
                aliases.difference_update(getattr(other, fd.name))

    def copy(self) -> "AliasUnion":
        copied = AliasUnion()
        copied.update(self)
        return copied

    def clear(self) -> None:
        for aliases in self:
            aliases.clear()
        self.IS_FULL_CV = True
        self.USE_END_V = False

    def __iter__(self) -> Iterator[set[Alias] | VcSet]:
        for fd in fields(self):
            aliases = getattr(self, fd.name)
            if not isinstance(aliases, bool):
                yield aliases

    def __contains__(self, alias: Alias) -> bool:
        match alias.type:
            case AliasType.C:
                return alias in self.c
            case AliasType.C_HEAD:
                return alias in self.c_head
            case AliasType.CV, AliasType.CV_LONG:
                return alias in self.cv
            case AliasType.CV_HEAD:
                return alias in self.cv_head
            case AliasType.V:
                return alias in self.v
            case AliasType.VC:
                return alias in self.vc
            case AliasType.VCV:
                return alias in self.vcv

        for fd in self.__dataclass_fields__.values():
            try:
                if alias in fd.value:
                    return True
            except TypeError:
                continue
        return False


@dataclass
class CvvWorkshop:
    cvv_set: set[Cvv] = field(default_factory=set)
    cvv_dict: dict[str, Cvv] = field(default_factory=dict)
    cv_dict: dict[str, list[Cvv]] = field(default_factory=dict)
    c_dict: dict[str, list[Cvv]] = field(default_factory=dict)
    v_dict: dict[str, list[Cvv]] = field(default_factory=dict)
    end_v_dict: dict[str, list[Cvv]] = field(default_factory=dict)
    redirect_consonant_dict: dict[str, list[str]] = field(default_factory=dict)
    redirect_vowel_dict: dict[str, list[str]] = field(default_factory=dict)

    def read_dict(self, dict_dir: str) -> None:
        with open(dict_dir, mode="r", encoding="utf-8") as fp:
            for line in fp.read().splitlines():
                if line := line.strip():
                    word = Cvv.new(re.split(r" *[,;\t，；] *", line))
                    cvv, c, v, *_ = word
                    self.cvv_set.add(word)
                    self.cvv_dict.setdefault(cvv, word)
                    if word.cv:
                        self.cv_dict.setdefault(word.cv, []).append(word)
                    self.c_dict.setdefault(c, []).append(word)
                    self.v_dict.setdefault(v, []).append(word)
                    self.end_v_dict.setdefault(word.get_v(use_end_v=True), []).append(
                        word
                    )

    def read_presamp(self, presamp_dir: str) -> None:
        """read presamp.ini file, do not support simplified format.
        simplified means word A does not shows up in CONSONANT section or neither.

        Args:
            presamp_dir (str): presamp.ini file path
        """
        presamp_config = configparser.ConfigParser(allow_no_value=True)
        presamp_config.optionxform = str  # type: ignore
        try:
            presamp_config.read(presamp_dir, encoding="utf-8")
        except configparser.MissingSectionHeaderError as e:
            raise EncodingWarning(
                f"Following error appear: \n{e}\n"
                f"It might be encoding error, please use utf-8 encoding."
            )

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
                    f"{cv} seems to appeared in [VOWEL] section or [CONSONANT] section multiple times."
                )
            elif len(component) == 1:
                v = c = component[0]
            else:
                v, c = component
            cvv = Cvv.new((cv, c, v))
            self.cvv_set.add(cvv)
            self.cvv_dict.setdefault(cv, cvv)
            if cvv.alias_c:
                self.c_dict.setdefault(cvv.alias_c, []).append(cvv)
            if cvv.alias_v:
                self.v_dict.setdefault(cvv.alias_v, []).append(cvv)
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
        if cvv:
            if cv := self.cvv_dict.get(cvv):
                return cv
            else:
                if cv_list := self.cv_dict.get(cvv):
                    return random.choice(cv_list)
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
                return random.choice(cvv_list)
            else:
                raise CantFindCvvError(f"no cvv has consonant of {c}")
        if v and not c:
            if cvv_list := self.v_dict.get(v):
                if exception:
                    new_cvv_list: list[Cvv] = []
                    for cv in cvv_list:
                        if cv.c not in exception:
                            new_cvv_list.append(cv)
                    cvv_list = new_cvv_list
                return random.choice(cvv_list)
            else:
                if cvv_list := self.end_v_dict.get(v):
                    if exception:
                        new_cvv_list: list[Cvv] = []
                        for cv in cvv_list:
                            if cv.c not in exception:
                                new_cvv_list.append(cv)
                        cvv_list = new_cvv_list
                    return random.choice(cvv_list)
                raise CantFindCvvError(f"no cvv has vowel {v}")
        if c and v:
            if cvv_list := self.c_dict.get(c):
                for cv in cvv_list:
                    if cv.get_lsd_v() == v:
                        return cv
                else:
                    raise CantFindCvvError(f"no cvv has {c} and {v} at the same time")
            else:
                for cv in self.cvv_set:
                    if cv.get_lsd_c() == c and cv.get_lsd_v() == v:
                        return cv
                else:
                    raise CantFindCvvError(f"no cvv has {c} and {v} at the same time")
        raise ArgumentTypeError("invalid arguments are given")

    def find_inner(self, v: str, c: str) -> Cvv:
        for cvv in self.cvv_set:
            if cvv.mid_v == v and cvv.end_v == c:
                return cvv
        raise CantFindCvvError(f"no cvv has {v} and {c} connection within it")

    def find_next(self, vc: tuple[str, str], vc_max_v: str) -> Cvv:
        try:
            return self.find_cvv(c=vc[1], v=vc_max_v)
        except CantFindCvvError:
            raise CantFindNextCvvError

    def _find_next(self, vc: tuple[str, str], vc_max_v: str) -> Cvv:
        try:
            return self.find_cvv(c=vc[1], v=vc_max_v)
        except CantFindCvvError:
            return self.find_cvv(c=vc[1])

    def read_redirect_config(self, redirect_config_dir) -> None:
        redirect_config = configparser.ConfigParser(allow_no_value=True)
        redirect_config.read(redirect_config_dir, encoding="utf-8")
        try:
            for key, values in redirect_config["VOWEL"].items():
                self.redirect_vowel_dict.setdefault(key, []).extend(values.split(","))
        except KeyError:
            pass
        try:
            for key, values in redirect_config["CONSONANT"].items():
                self.redirect_consonant_dict.setdefault(key, []).extend(
                    values.split(",")
                )
        except KeyError:
            pass

    def get_redirect_phoneme(self, phoneme: tuple[str, str, AliasType]) -> list[str]:
        redirect_phoneme: list[str] = []
        _, _, alias_type = phoneme
        if alias_type == AliasType.C_HEAD:
            return redirect_phoneme

        elif alias_type in (AliasType.CV, AliasType.CV_LONG):
            c, v, _ = phoneme
            cvv = self.find_cvv(c=c, v=v)
            if cvv.cv:
                for cvv in self.cv_dict.get(cvv.cv, []):
                    _, alias_c, alias_v = cvv.get_lsd_cvv()
                    if (cv := f"{alias_c} {alias_v}") != f"{c} {v}":
                        redirect_phoneme.append(cv)

        elif alias_type == AliasType.VC:
            v, c, _ = phoneme
            if c in self.v_dict:
                redirect_consonant_dict = self.redirect_vowel_dict
            else:
                redirect_consonant_dict = self.redirect_consonant_dict

            for redirect_vowel in self.redirect_vowel_dict.get(v, []):
                redirect_phoneme.append(f"{redirect_vowel} {c}")

            for redirect_consonant in redirect_consonant_dict.get(c, []):
                redirect_phoneme.append(f"{v} {redirect_consonant}")

            for redirect_vowel in self.redirect_vowel_dict.get(v, []):
                for redirect_consonant in redirect_consonant_dict.get(c, []):
                    redirect_phoneme.append(f"{redirect_vowel} {redirect_consonant}")

        elif alias_type == AliasType.V:
            v, *_ = phoneme
            for redirect_vowel in self.redirect_vowel_dict.get(str(phoneme), []):
                redirect_phoneme.append(f"{redirect_vowel} ")

        else:
            raise ArgumentTypeError("type of given alias is wrong")
        return redirect_phoneme

    def get_presamp_str(self) -> str:
        presamp_ini: list[str] = ["[VERSION]\n" "1.7"]
        presamp_ini.append("[VOWEL]")
        for v, cvv_list in self.v_dict.items():
            v_str = ",".join(str(cvv) for cvv in cvv_list if cvv.v == v)
            v_str = f"{v}={v}={v_str}=100"
            presamp_ini.append(v_str)
        presamp_ini.append("[CONSONANT]")
        for c, cvv_list in self.c_dict.items():
            c_str = ",".join(str(cvv) for cvv in cvv_list if cvv.c == c)
            c_str = f"{c}={c_str}=1"
            presamp_ini.append(c_str)
        presamp_ini.append("[ENDTYPE]\n" "%v% R\n" "[ENDFLAG]\n" "1")
        return "\n".join(presamp_ini)

    def get_lsd_str(self) -> str:
        lsd_str = []
        for cvv in sorted(self.cvv_set, key=Cvv.get_lsd_c):
            cv, c, v = cvv.get_lsd_cvv()
            if c == v:
                lsd_str.append(f"{cv}\n#{v}")
            else:
                lsd_str.append(f"{cv}\n{c}#{v}")
        return "\n".join(lsd_str)

    def save_presamp(self, presamp_dir: str) -> None:
        with open(presamp_dir, mode="w", encoding="utf-8") as f:
            f.write(self.get_presamp_str())

    def save_lsd(self, lsd_dir: str) -> None:
        with open(lsd_dir, mode="w", encoding="utf-8") as f:
            f.write(self.get_lsd_str())

    def get_simplified_cv(self) -> list[tuple[str, str]]:
        """return a list that contain (simplified cv, full cv)"""
        cv_list = []
        for key, values in self.cv_dict.items():
            for value in values:
                cv_list.append((key, value.cvv))
        return cv_list
