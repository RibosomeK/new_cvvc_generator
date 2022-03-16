import configparser
import re
from typing import Optional
from .cvv_dataclasses import AliasType, CvvWorkshop, VcSet, AliasUnion
from .errors import AliasConfigTypeError, AliasNotExistError, AliasTypeError, CantFindCvvError


class AliasUnionGenerator:
    """get needed alias."""
    
    def __init__(self, cvv_workshop: CvvWorkshop) -> None:
        self.cvv_workshop = cvv_workshop
    
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
        alias_union.vc = VcSet()
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
        for alias_type, alias_str in config["UNNEEDED"].items():
            if not alias_str or alias_str.upper() == "NONE":
                continue 
            alias_pack = self.split_type_and_alias(alias_str)
            if alias_type == "cv_head" or alias_type == "cv":
                
                for cv in alias_str.split(","):
                    if self.cvv_workshop.find_cvv(cvv=cv):
                        unneeded.__dict__[cv].add(cv)
                    elif cv in self.cvv_workshop.c_dict:
                        unneeded.__dict__[cv].update(
                            cvv.get_cv(is_full_cv) for cvv in self.cvv_workshop.c_dict[cv]
                        )
                    else:
                        raise ValueError
            elif alias_type == "vc":
                for vc in alias_str.split(","):
                    if vc in self.cvv_workshop.c_dict:
                        unneeded.vc.update((v, vc) for v in self.cvv_workshop.v_dict)
                    if vc in self.cvv_workshop.v_dict:
                        unneeded.vc.update((vc, c) for c in self.cvv_workshop.c_dict)
                    elif " " in vc:
                        unneeded.vc.add(tuple(vc.split(" ")))
                    else:
                        raise ValueError
            elif alias_type == "vr":
                unneeded.vr.update(alias_str.split(","))
            elif alias_type == "c_head":
                unneeded.c_head.update(alias_str.split(","))
            elif alias_type == "vcv":
                for vcv in alias_str.split(","):
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

    def split_type_and_alias(self, alias_str: str) -> list[tuple[AliasType, list[str]]]:
        """spliting string like 'c: c1, c2...; cv: cv1, cv2...' into
        [(AliasType.C, [c1, c2, ...]),
         (AliasType.CV, [cv1, cv2, ...])

        """
        alias_pack = []
        type_: AliasType
        type_sections = re.split(r' *; *', alias_str)
        
        for section in type_sections:
            alias_type, alias = re.split(r' *: *', section)
            match alias_type.upper():
                case 'C':
                    type_ = AliasType.C
                case 'CV':
                    type_ = AliasType.CV    
                case 'V':
                    type_ = AliasType.V
                case 'VC':
                    type_ = AliasType.VC
                case 'VCV':
                    type_ = AliasType.VCV
                case _:
                    raise AliasConfigTypeError(f'wrong alias type {alias_type}')
            alias_pack.append((type_, re.split(r' *, *', alias)))
        
        return alias_pack
    
    def get_c_alias(self, alias_pack: list[tuple[AliasType, list[str]]]) -> set[str]:
        """return a consonant set from alias pack"""
        
        c_set = set()
        for type_, alias_list in alias_pack:
            if type_ != AliasType.C:
                raise AliasTypeError(f'{type_} does not exist')
            for alias in alias_list:
                if alias not in self.cvv_workshop.c_dict:
                    raise AliasNotExistError(f'{alias} does not exist in given config')
                c_set.add(alias)
        return c_set
    
    def get_cv_alias(self, alias_pack: list[tuple[AliasType, list[str]]]) -> set[str]:
        """return a cv set from given alias pack"""
        
        cv_set = set()
        for type_, alias_list in alias_pack:
            if type_ == AliasType.C:
                for alias in alias_list:
                    try:
                        cvv = self.cvv_workshop.find_cvv(c=alias)
                        cv_set.add(cvv.get_cv())
                    except CantFindCvvError:
                        raise AliasNotExistError(f'no cvv has consonant {alias}')
            elif type_ == AliasType.CV:
                for alias in alias_list:
                    if (alias not in self.cvv_workshop.cvv_dict and 
                        alias not in self.cvv_workshop.cv_dict):
                        raise AliasNotExistError(f'word {alias} does not exist')
                    cv_set.add(alias)
            else:
                raise AliasTypeError(f'{type_} does not exist')
        return cv_set
    
    def get_vc_alias(self, alias_pack: list[tuple[AliasType, list[str]]]) -> set[tuple[str, str]]:
        """return a vc set from given alias pack"""
        
        vc_set = set()
        for type_, alias_list in alias_pack:
            if type_ == AliasType.C:
                pass
        
        return vc_set