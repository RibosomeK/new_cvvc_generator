from dataclasses import dataclass
import re
from cvvc_reclist_generator import (
    CvvWorkshop, AliasUnionGenerator, ReclistGenerator, 
    ReclistChecker, OtoGenerator, VsdxmfGenerator
    )


@dataclass
class Parameters:
    dict_file: str
    alias_config: str
    redirect_config: str
    save_path: str
    
    is_two_mora: bool
    is_haru_style: bool
    is_mora_x: bool
    
    length: int
    is_full_cv: bool
    is_cv_head: bool
    is_c_head: bool
    cv_mid: str
    
    bpm: float
    blank_beat: int
    
    do_save_oto: bool
    do_save_reclist: bool
    do_save_presamp: bool
    do_save_vsdxmf: bool
    do_save_lsd: bool


class CvvcReclistGeneratorModel:
    
    def __init__(self, parameters: Parameters):
        self.cvv_workshop = CvvWorkshop()
        self.parameters = parameters
        
        if parameters.dict_file.endswith('txt'):
            self.cvv_workshop.read_dict(parameters.dict_file)
        elif parameters.dict_file.endswith('ini'):
            self.cvv_workshop.read_presamp(parameters.dict_file)
        elif parameters.dict_file.endswith('lsd'):
            self.cvv_workshop.read_lsd(parameters.dict_file)
        
        if parameters.redirect_config:
            self.cvv_workshop.read_redirect_config(parameters.redirect_config)
            
        self.alias_union_generator = AliasUnionGenerator(self.cvv_workshop)
        if parameters.alias_config:
            alias_config = parameters.alias_config
        else:
            alias_config = None
        alias_union = self.alias_union_generator.get_needed_alias(
            parameters.is_c_head, 
            parameters.is_cv_head,
            parameters.is_full_cv,
            alias_config
        )
        
        if parameters.cv_mid:
            cv_mid = re.split(r'[;,\s]\s*', parameters.cv_mid)
        else:
            cv_mid = None
        
        self.reclist_generator = ReclistGenerator(self.cvv_workshop)
        if parameters.is_haru_style:
            rest_alias = self.reclist_generator.gen_plan_b(alias_union.copy())
        else:
            rest_alias = alias_union.copy()
        if parameters.is_two_mora:
            self.reclist_generator.gen_2mora(rest_alias)
        elif parameters.is_mora_x or parameters.length:
            self.reclist_generator.gen_mora_x(rest_alias, parameters.length, cv_mid)

        self.oto_generator = OtoGenerator()
        if parameters.do_save_oto:
            self.oto_generator.gen_oto(
                self.reclist_generator.reclist, 
                alias_union.copy(),
                parameters.bpm,
                parameters.is_full_cv,
                cv_mid
         )
        
        self.vsdxmf_generator = VsdxmfGenerator(self.cvv_workshop)
        if parameters.do_save_vsdxmf:
            self.vsdxmf_generator.gen_vsdxmf(
                self.reclist_generator.reclist,
                alias_union.copy(),
                parameters.bpm,
                parameters.is_full_cv,
                cv_mid
            )
            
    def get_reclist_str(self) -> str | None:
        return str(self.reclist_generator.reclist) or None
    
    def get_oto_str(self) -> str | None:
        return str(self.oto_generator.oto_union) or None
    
    def get_presamp_str(self) -> str | None:
        return str(self.cvv_workshop.get_presamp_str()) or None
    
    def get_vsdxmf_str(self) -> str | None:
        return str(self.vsdxmf_generator.vsdxmf_union) or None
    
    def get_lsd_str(self) -> str | None:
        return str(self.cvv_workshop.get_lsd_str()) or None
    
    def save_reclist(self) -> None:
        self.reclist_generator.save_reclist(self.parameters.save_path + '/reclist.txt')
        
    def save_oto(self) -> None:
        self.oto_generator.save_oto(self.parameters.save_path + '/oto.ini')
        
    def save_presamp(self) -> None:
        self.cvv_workshop.save_presamp(self.parameters.save_path + '/presamp.ini')
        
    def save_vsdxmf(self) -> None:
        self.vsdxmf_generator.save_vsdxmf(self.parameters.save_path + '/vsdxmf.vsdxmf')
        
    def save_lsd(self) -> None:
        self.cvv_workshop.save_lsd(self.parameters.save_path + '/lsd.lsd')
        