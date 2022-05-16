from dataclasses import dataclass
import os
from sqlite3 import paramstyle
from typing import Any, Optional
from configparser import ConfigParser
from unicodedata import name

from .cvv_dataclasses import AliasUnion, CvvWorkshop, OtoUnion, Reclist, VsdxmfUnion
from .alias_union_generator import AliasUnionGenerator
from .reclist_generator import ReclistGenerator
from .reclist_checker import ReclistChecker
from .oto_generator import OtoGenerator
from .vsdxmf_generator import VsdxmfGenerator
from .simplified_cv_replication_json_generator import CvReplicationJsonGenerator
from .errors import (
    AliasConfigNotFoundError,
    ConfigError,
    ConfigNotFoundError,
    RedirectConfigNotFoundError,
    DictfileNotFoundError
)

PARAMETERS = (
    "dict_file",
    "alias_config",
    "redirect_config",
    "save_path",
    "is_two_mora",
    "is_haru_style",
    "is_mora_x",
    "length",
    "is_full_cv",
    "is_cv_head",
    "is_c_head_4_utau",
    "bpm",
    "blank_beat",
    "do_save_reclist",
    "do_save_oto",
    "do_save_presamp",
    "do_save_vsdxmf",
    "do_save_lsd",
)
TRUE_VALUE = ("true", "yes", "1", "y", "t", "yeah", "yup")
NONE_VALUE = ("none", "null", "no", "false", "0", "n")


class Parameters:
    def __init__(self):
        self.dict_file: str = ""
        self.alias_config: str = ""
        self.redirect_config: str = ""
        self.save_path: str = "./result"

        self.is_two_mora: bool = False
        self.is_haru_style: bool = False
        self.is_mora_x: bool = False

        self.length: int = 3
        self.is_full_cv: bool = True
        self.is_cv_head: bool = True
        self.is_c_head_4_utau: bool = False

        self.bpm: float = 130
        self.blank_beat: int = 2

        self.do_save_oto: bool = True
        self.do_save_reclist: bool = False
        self.do_save_presamp: bool = False
        self.do_save_vsdxmf: bool = False
        self.do_save_lsd: bool = False

    def __getitem__(self, key) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key, value) -> None:
        """value can change but new key can not be added"""

        if key not in PARAMETERS:
            raise KeyError(f"You can not set new key: {key}")

        if self.__dict__.get(key, None) is None:
            self.__dict__[key] = value
            return

        if isinstance(value, type(self[key])):

            if isinstance(self[key], str) and value.lower() in NONE_VALUE:
                self.__dict__[key] = None
            else:
                self.__dict__[key] = value

        elif isinstance(self[key], int) and not isinstance(self[key], bool):
            try:
                self.__dict__[key] = int(value)
            except ValueError:
                raise ValueError(f"invalid number: {value} in key: {key}")

        elif value.lower() in TRUE_VALUE:
            self.__dict__[key] = True
        else:
            self.__dict__[key] = False

    def __setattr__(self, __name: str, __value: Any) -> None:
        self[__name] = __value

    def update(self, other) -> None:
        """use a dict or dict like object to update parameters"""
        for key, value in other.items():
            try:
                self[key] = value
            except KeyError:
                print(f"unknown parameter name: {key}")

    def load_config(self, config_path: str) -> None:
        """load a config ini"""

        config = ConfigParser()
        config.read(config_path, encoding="utf-8")

        try:
            self.update(config["PARAMETERS"])
        except KeyError:
            raise ConfigNotFoundError

    def export_config(self, config_path: str = "./config/config.ini") -> None:
        """export current parameters as an ini config"""
        config = ConfigParser()
        config["PARAMETERS"] = self.__dict__

        with open(config_path, mode="w", encoding="utf-8") as fp:
            config.write(fp)


class CvvcReclistGenerator:
    """a cvvc reclist generator model"""

    def __init__(self) -> None:
        self.parameters: Parameters = Parameters()
        self.cvv_workshop: CvvWorkshop = CvvWorkshop()

        self.alias_union: AliasUnion
        self.reclist: Reclist
        self.oto: OtoUnion
        self.vsdxmf: VsdxmfUnion

    def load_config(self, config_path: Optional[str] = None) -> None:
        """load config"""

        if config_path:
            self.parameters.load_config(config_path)
        else:
            for root, _, files in os.walk(".", topdown=False):
                for name in files:
                    if name == "config.ini":
                        return self.parameters.load_config(os.path.join(root, name))
            else:
                raise ConfigNotFoundError("Can not find config file.")

    def setup_cvv_workshop(self) -> None:
        
        try:
            self.cvv_workshop.read_dict(self.parameters.dict_file)
        except FileNotFoundError:
            raise DictfileNotFoundError(f"Can not find dict file: {self.parameters.dict_file}")
            
        if self.parameters.redirect_config:
            try:
                self.cvv_workshop.read_redirect_config(self.parameters.redirect_config)
            except FileNotFoundError:
                raise RedirectConfigNotFoundError("Cant find redirect config")

    def get_alias(self) -> None:

        alias_union_generator = AliasUnionGenerator(self.cvv_workshop)

        try:
            self.alias_union = alias_union_generator.get_needed_alias(
                is_c_head=True,
                is_cv_head=self.parameters.is_cv_head,
                is_full_cv=self.parameters.is_full_cv,
                alias_config=self.parameters.alias_config,
            )
        except FileNotFoundError:
            raise AliasConfigNotFoundError("cant find alias config")

    def get_reclist(self) -> None:
        generator = ReclistGenerator(self.cvv_workshop)
        alias_union = self.alias_union.copy()

        if not (self.parameters.is_c_head_4_utau or self.parameters.do_save_vsdxmf):
            alias_union.c_head.clear()

        if self.parameters.is_haru_style:
            alias_union = generator.gen_plan_b(alias_union)

        if self.parameters.is_mora_x and self.parameters.is_two_mora:
            raise ConfigError("two mora and mora x cant be same")

        if self.parameters.is_mora_x:
            generator.gen_mora_x(alias_union, self.parameters.length)
        else:
            generator.gen_2mora(alias_union)

        self.reclist = generator.reclist

    def get_oto(self):
        generator = OtoGenerator()
        alias_union = self.alias_union.copy()

        if not self.parameters.is_c_head_4_utau:
            alias_union.c_head.clear()

        generator.gen_oto(self.reclist, alias_union, self.parameters.bpm)
        self.oto = generator.oto_union

    def get_vsdxmf(self):
        generator = VsdxmfGenerator(self.cvv_workshop)
        alias_union = self.alias_union.copy()

        generator.gen_vsdxmf(self.reclist, alias_union, self.parameters.bpm)
        self.vsdxmf = generator.vsdxmf_union

    def save_reclist(self, reclist_path: Optional[str] = "./result/reclist.txt"):
        if reclist_path is None:
            reclist_path = f"{self.parameters.save_path}/reclist.txt"

        ReclistGenerator.export_reclist(self.reclist, reclist_path)

    def save_oto(self, oto_path: Optional[str] = "./result/oto.ini"):
        if oto_path is None:
            oto_path = f"{self.parameters.save_path}/oto.ini"
        OtoGenerator.export_oto(self.oto, oto_path)

    def save_presamp(self, presamp_path: Optional[str] = "./result/presamp.ini"):
        if presamp_path is None:
            presamp_path = f"{self.parameters.save_path}/presamp.ini"
        self.cvv_workshop.save_presamp(presamp_path)

    def generate(self, config_path: Optional[str] = None) -> None:
        """generate reclist and add-ons accroding to config"""

        self.load_config(config_path)
        self.setup_cvv_workshop()
        self.get_alias()
        self.get_reclist()
        print("reclist generate success...")
        self.get_oto()
        print("oto generate success...")
        self.save_reclist()
        print("reclist exported...")
        self.save_oto()
        print("oto exported...")
        self.save_presamp()
        print("presamp.ini exported...")
