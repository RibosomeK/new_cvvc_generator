from dataclasses import dataclass, field, fields
from cvvc_reclist_generator import (
    AliasUnionGenerator,
    ReclistGenerator,
    OtoGenerator,
    VsdxmfGenerator,
)
from cvvc_reclist_generator.data_struct import CvvWorkshop, LabelUnion


@dataclass
class Parameters:
    dict_file: str = ""
    alias_config: str = ""
    redirect_config: list[str] = field(default_factory=list)
    save_path: str = "./result"

    is_two_mora: bool = False
    is_haru_style: bool = False
    is_mora_x: bool = False

    length: int = 3
    is_full_cv: bool = True
    is_cv_head: bool = True
    is_c_head_4_utau: bool = False

    order_by: int = 0
    is_order_length_switch: bool = False
    order_length: int = 3

    bpm: float = 130
    blank_beat: int = 2

    do_save_oto: bool = False
    do_save_reclist: bool = True
    do_save_presamp: bool = False
    do_save_vsdxmf: bool = False
    do_save_lsd: bool = False

    def __post_init__(self):
        for key, fd in self.__dataclass_fields__.items():
            value = getattr(self, key)
            self[key] = value
            
    def __setitem__(self, key, value):
        is_miss_type = False
        fd = self.__dataclass_fields__[key]
        try:
            if not (
                isinstance(value, fd.type)
                or isinstance(value, (int, float))
            ):
                is_miss_type = True
        except TypeError:
            if not isinstance(value, fd.type.__origin__):
                is_miss_type = True

        if is_miss_type:
            setattr(self, key, fd.default)
            print(f"Invalid value: {value} for key: {key}")
            print(f"Fallback to default: {fd.default}")

        setattr(self, key, value)

    def __getitem__(self, key: str):
        return getattr(self, key)


class CvvcReclistGeneratorModel:
    def __init__(self, parameters: Parameters):
        self.cvv_workshop = CvvWorkshop()
        self.parameters = parameters

        if parameters.dict_file.endswith("txt"):
            self.cvv_workshop.read_dict(parameters.dict_file)
        elif parameters.dict_file.endswith("ini"):
            self.cvv_workshop.read_presamp(parameters.dict_file)
        elif parameters.dict_file.endswith("lsd"):
            self.cvv_workshop.read_lsd(parameters.dict_file)

        if redirect_configs := parameters.redirect_config:
            for config in redirect_configs:
                self.cvv_workshop.read_redirect_config(config)

        self.alias_union_generator = AliasUnionGenerator(self.cvv_workshop)
        if parameters.alias_config:
            alias_config = parameters.alias_config
        else:
            alias_config = None

        if parameters.is_c_head_4_utau or parameters.do_save_vsdxmf:
            is_c_head = True
        else:
            is_c_head = False
        alias_union = self.alias_union_generator.get_needed_alias(
            is_c_head,
            parameters.is_cv_head,
            parameters.is_full_cv,
            True,
            alias_config,
        )

        alias_union_4_utau = alias_union.copy()
        if not parameters.is_c_head_4_utau:
            alias_union_4_utau.c_head.clear()

        self.reclist_generator = ReclistGenerator(
            self.cvv_workshop, parameters.order_by
        )
        if parameters.is_haru_style:
            rest_alias = self.reclist_generator.gen_plan_b(alias_union.copy())
        else:
            rest_alias = alias_union.copy()
        if parameters.is_two_mora:
            self.reclist_generator.gen_2mora(rest_alias)
        elif parameters.is_mora_x or parameters.length:
            if parameters.is_order_length_switch:
                self.reclist_generator.gen_mora_x(
                    rest_alias, parameters.length, parameters.order_length
                )
            else:
                self.reclist_generator.gen_mora_x(
                    rest_alias, parameters.length, parameters.length
                )

        self.oto_generator = OtoGenerator()
        if parameters.do_save_oto:
            self.oto_generator.gen_oto(
                self.reclist_generator.reclist,
                alias_union_4_utau.copy(),
                parameters.bpm,
            )
            if parameters.blank_beat != 2:
                self.shift_labels(self.oto_generator.oto_union)

        self.vsdxmf_generator = VsdxmfGenerator(self.cvv_workshop)
        if parameters.do_save_vsdxmf:
            self.vsdxmf_generator.gen_vsdxmf(
                self.reclist_generator.reclist, alias_union.copy(), parameters.bpm
            )
            if parameters.blank_beat != 2:
                self.shift_labels(self.vsdxmf_generator.vsdxmf_union)

    def shift_labels(self, label_union: LabelUnion):
        shift = (self.parameters.blank_beat - 2) * 4.2 * self.parameters.bpm
        for label in label_union:
            label.shift(round(shift))

    def get_reclist_str(self) -> str:
        return str(self.reclist_generator.reclist)

    def get_oto_str(self) -> str:
        return str(self.oto_generator.oto_union)

    def get_presamp_str(self) -> str:
        return str(self.cvv_workshop.get_presamp_str())

    def get_vsdxmf_str(self) -> str:
        return str(self.vsdxmf_generator.vsdxmf_union)

    def get_lsd_str(self) -> str:
        return str(self.cvv_workshop.get_lsd_str())

    def save_reclist(self) -> None:
        self.reclist_generator.save_reclist(self.parameters.save_path + "/reclist.txt")

    def save_oto(self) -> None:
        self.oto_generator.save_oto(self.parameters.save_path + "/oto.ini")

    def save_presamp(self) -> None:
        self.cvv_workshop.save_presamp(self.parameters.save_path + "/presamp.ini")

    def save_vsdxmf(self) -> None:
        self.vsdxmf_generator.save_vsdxmf(self.parameters.save_path + "/vsdxmf.vsdxmf")

    def save_lsd(self) -> None:
        self.cvv_workshop.save_lsd(self.parameters.save_path + "/lsd.lsd")
