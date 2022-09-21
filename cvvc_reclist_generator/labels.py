from ast import alias
from collections import namedtuple
from dataclasses import dataclass
from ipaddress import v4_int_to_packed
from re import S
from typing import Iterator, NamedTuple


@dataclass
class Digits:
    lft: float
    con: float
    rft: float
    pre: float
    ovl: float

    def __str__(self) -> str:
        return ",".join(f"{digit:.1f}" for digit in self)

    def __iter__(self) -> Iterator[float]:
        return iter((self.lft, self.con, self.rft, self.pre, self.ovl))


class UDigits(Digits):
    """utau specific"""


class VDigits(Digits):
    """vs specific"""

    def __iter__(self) -> Iterator[float]:
        return iter((self.lft, self.pre, self.con, self.rft, self.ovl))

    def __str__(self) -> str:
        if any(self):
            return Digits.__str__(self)
        else:
            return ",".join(f"{digit}" for digit in self)


@dataclass
class Label:
    """a universal label for oto and vs oto"""

    wav: str
    prefix: str
    alias: str
    suffix: str
    digits: Digits


class Oto(Label):
    """single line of oto"""

    __slot__ = ()

    def __init__(
        self,
        wav: str,
        prefix: str,
        alias: str,
        suffix: str,
        lft: float,
        con: float,
        rft: float,
        pre: float,
        ovl: float,
    ):
        self.wav = wav
        self.prefix = prefix
        self.alias = alias
        self.suffix = suffix
        self.digits = UDigits(lft, con, rft, pre, ovl)

    def __str__(self) -> str:
        alias = self.alias

        if self.prefix:
            alias = self.prefix + alias
        if self.suffix:
            alias += self.suffix

        return f"{self.wav}={self.alias},{self.digits}"

    @property
    def lft(self) -> float:
        return self.digits.lft

    @property
    def con(self) -> float:
        return self.digits.con

    @property
    def rft(self) -> float:
        return self.digits.rft

    @property
    def pre(self) -> float:
        return self.digits.pre

    @property
    def ovl(self) -> float:
        return self.digits.ovl


class Vsdxmf(Label):

    __slot__ = ()

    def __init__(
        self,
        phoneme: str,
        wav: str,
        lft: float,
        pre: float,
        con: float,
        rft: float,
        ovl: float,
    ) -> None:
        self.phoneme = phoneme
        self.wav = wav
        self.alias, self.prefix, self.suffix = "", "", ""
        self.digits = VDigits(lft, con, rft, pre, ovl)

    def __str__(self) -> str:
        return f"{self.phoneme},{self.wav},{self.digits}"

    @staticmethod
    def get_redirect(phoneme: str, redirect_phoneme: str) -> "Vsdxmf":
        return Vsdxmf(phoneme, f"#{redirect_phoneme}", 0, 0, 0, 0, 0)
    
    @property
    def lft(self) -> float:
        return self.digits.lft

    @property
    def con(self) -> float:
        return self.digits.con

    @property
    def rft(self) -> float:
        return self.digits.rft

    @property
    def pre(self) -> float:
        return self.digits.pre

    @property
    def ovl(self) -> float:
        return self.digits.ovl

def shift_label(label: Label, shifts: int) -> Label:
    """to shift the label left or right for whole. left is negative."""
    new_digits = UDigits(*[digit + shifts for digit in label.digits])
    label.digits = new_digits
    return label
