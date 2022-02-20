from cvv_dataclasses import *
from alias_union_generator import AliasUnionGenerator
from reclist_generator import ReclistGenerator
from reclist_checker import ReclistChecker
from oto_generator import OtoGenerator
from vsdxmf_generator import VsdxmfGenerator

def main():
    cvv_workshop = CvvWorkshop()
    cvv_workshop.read_dict('./dict_files/CHN_extendForVS.txt')
    cvv_workshop.read_redirect_config('./config/redirect.ini')
    
    alias_union_generator = AliasUnionGenerator(cvv_workshop)
    alias_union = alias_union_generator.get_needed_alias(
        is_c_head=True, is_cv_head=True, is_full_cv=True, alias_config='./config/alias_config.ini')
    alias_union_backup = alias_union.copy()
    
    generator = ReclistGenerator(cvv_workshop)
    generator.gen_mora_x(
        alias_union=generator.gen_plan_b(alias_union), length=8, cv_mid=None)
    reclist = generator.reclist
    
    reclist_checker = ReclistChecker(reclist=reclist, alias_union=alias_union_backup.copy())
    reclist_checker.check()
    
    oto_generator = OtoGenerator()
    alias_union_utau = alias_union_backup.copy()
    alias_union_utau.c_head.clear()
    oto_generator.gen_oto(
        reclist=reclist, alias_union=alias_union_utau, bpm=120, is_full_cv=True, cv_mid=None)
    
    vsdxmf_generator = VsdxmfGenerator(cvv_workshop)
    alias_union_vs = alias_union_backup.copy()
    vsdxmf_generator.gen_vsdxmf(
        reclist=reclist, alias_union=alias_union_vs, bpm=120, cv_mid=None)
    
    generator.save_reclist('./result/reclist.txt')
    oto_generator.save_oto('./result/oto.txt')
    vsdxmf_generator.save_vsdxmf('./result/vsdxmf.vsdxmf')
    cvv_workshop.save_presamp('./result/presamp.ini')
    cvv_workshop.save_lsd('./result/lsd.lsd')
    

if __name__ == "__main__":
    main()