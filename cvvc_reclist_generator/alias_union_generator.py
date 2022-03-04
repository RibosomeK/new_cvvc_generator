import configparser
from typing import Optional
from .cvv_dataclasses import CvvWorkshop, VcSet, AliasUnion


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
