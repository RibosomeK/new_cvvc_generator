from dataclasses import dataclass
from typing import Any, Optional
from configparser import ConfigParser

from .cvv_dataclasses import AliasUnion, CvvWorkshop, OtoUnion, Reclist
from .alias_union_generator import AliasUnionGenerator
from .reclist_generator import ReclistGenerator
from .reclist_checker import ReclistChecker
from .oto_generator import OtoGenerator
from .vsdxmf_generator import VsdxmfGenerator
from .simplified_cv_replication_json_generator import CvReplicationJsonGenerator
from .errors import ConfigError
from cvvc_reclist_generator import alias_union_generator


TRUE_VALUE = ("true", "yes", "1", "y", "t", "yeah", "yup")
NONE_VALUE = ("none", "null", "no", "false", "0", "n")


@dataclass(slots=True)
class Parameters:
    dict_file: str = ""
    alias_config: str = ""
    redirect_config: str = ""
    save_path: str = "./result"

    is_two_mora: bool = False
    is_haru_style: bool = False
    is_mora_x: bool = False

    length: int = 3
    is_full_cv: bool = True
    is_cv_head: bool = True
    is_c_head_4_utau: bool = False

    bpm: float = 130
    blank_beat: int = 2

    do_save_oto: bool = True
    do_save_reclist: bool = False
    do_save_presamp: bool = False
    do_save_vsdxmf: bool = False
    do_save_lsd: bool = False

    def __getitem__(self, key) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key, value) -> None:
        """value can change but new key can not be added"""

        if key not in self.__dict__:
            raise KeyError("You can not set new key")

        if isinstance(value, self[key]):

            if isinstance(self[key], str) and value.lower() in NONE_VALUE:
                self[key] = None
            else:
                self[key] = value

        elif isinstance(key[value], int):
            try:
                self[key] = int(value)
            except TypeError:
                raise TypeError(f"invalid number: {value}")

        elif key.lower() in TRUE_VALUE:
            self[key] = True
        else:
            self[key] = False

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

        self.update(config["PARAMETERS"])

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
        self.oto = OtoUnion

    def load_config(self, config_path: Optional[str] = None) -> None:
        """load config"""

        DEFAULT_CONFIG_PATH = ("./config.ini", "./config/config.ini")

        if config_path:
            self.parameters.load_config(config_path)
        else:
            for path in DEFAULT_CONFIG_PATH:
                try:
                    self.parameters.load_config(path)
                    break
                except FileNotFoundError:
                    continue
            else:
                raise FileNotFoundError("Can not find config file.")

    def setup_cvv_workshop(self) -> None:

        self.cvv_workshop.read_dict(self.parameters.dict_file)

        if self.parameters.redirect_config:
            self.cvv_workshop.read_redirect_config(self.parameters.redirect_config)

    def get_alias(self) -> None:

        alias_union_generator = AliasUnionGenerator(self.cvv_workshop)
        self.alias_union = alias_union_generator.get_needed_alias(
            is_c_head=True,
            is_cv_head=self.parameters.is_cv_head,
            is_full_cv=self.parameters.is_full_cv,
            alias_config=self.parameters.alias_config,
        )

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

    def generate(self, config_path: Optional[str] = None) -> None:
        """generate reclist and add-ons accroding to config"""

        self.load_config(config_path)
        self.setup_cvv_workshop()
        self.get_alias()
        self.get_reclist()
        self.get_oto()


def main():
    cvv_workshop = CvvWorkshop()
    cvv_workshop.read_dict("./dict_files/CHN_simplified_cv.txt")
    cvv_workshop.read_redirect_config("./config/redirect.ini")

    alias_union_generator = AliasUnionGenerator(cvv_workshop)
    alias_union = alias_union_generator.get_needed_alias(
        is_c_head=True,
        is_cv_head=True,
        is_full_cv=True,
        alias_config="./config/alias_config.ini",
    )
    alias_union_backup = alias_union.copy()

    generator = ReclistGenerator(cvv_workshop)
    generator.gen_mora_x(alias_union=generator.gen_plan_b(alias_union), length=8)
    reclist = generator.reclist

    reclist_checker = ReclistChecker(
        reclist=reclist, alias_union=alias_union_backup.copy()
    )
    reclist_checker.check()

    oto_generator = OtoGenerator()
    alias_union_utau = alias_union_backup.copy()
    alias_union_utau.c_head.clear()
    oto_generator.gen_oto(reclist=reclist, alias_union=alias_union_utau, bpm=120)

    vsdxmf_generator = VsdxmfGenerator(cvv_workshop)
    alias_union_vs = alias_union_backup.copy()
    vsdxmf_generator.gen_vsdxmf(reclist=reclist, alias_union=alias_union_vs, bpm=120)

    simplified_cv_list = cvv_workshop.get_simplified_cv()
    json_generator = CvReplicationJsonGenerator(
        CvReplicationJsonGenerator.get_json_rules(
            simplified_cv_list, patterns=["- {}", "{}_L"]
        )
    )

    if simplified_cv_list:
        json_generator.save_json(file_path="./result")

    generator.save_reclist("./result/reclist.txt")
    oto_generator.save_oto("./result/oto.ini")
    vsdxmf_generator.save_vsdxmf("./result/vsdxmf.vsdxmf")
    cvv_workshop.save_presamp("./result/presamp.ini")
    cvv_workshop.save_lsd("./result/lsd.lsd")
