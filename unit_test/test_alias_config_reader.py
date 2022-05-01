import sys
sys.path.append("")

from cvvc_reclist_generator.alias_union_generator import AliasUnionGenerator
from cvvc_reclist_generator.cvv_dataclasses import CvvWorkshop

def main():
    cvv_workshop = CvvWorkshop()
    cvv_workshop.read_dict("dict_files/CHN_extendForVS.txt")
    
    alias_union_generator = AliasUnionGenerator(cvv_workshop)
    a, b = alias_union_generator.read_alias_config("config/alias_config.json")
    print(a)
    print("-"*50)
    print(b)

if __name__ == "__main__":
    main()