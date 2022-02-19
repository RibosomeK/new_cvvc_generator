from collections import UserList, namedtuple
from typing import Optional, Iterable


class Cvv(namedtuple("Cvv", "cvv c v act_c fol_v cv mid_v end_v")):
    """
    take [gwaang] for example:
        cvv: gwaang
        c: k
        v: aang
        acl_c: khw (actual consonant)
        fol_v: waang (for VocalSharp)
        cv: gwA (does not include end_v)
        mid_v: aang (stretch part in lengthening a note)
        end_v: ng (the ended part)
    last three params are optional (None),
    """

    __slot__ = ()
    
    @staticmethod
    def new(components: Optional[Iterable[str]]=None) -> 'Cvv':
        length = 8
        if components is None:
            return Cvv(*[None]*length)
        else:
            param = []
            for idx, value in enumerate(components):
                if idx > length:
                    raise SyntaxError(f'More than {length} arguments are given.')
                if value == '':
                    value = None
                param.append(value)
            param.extend([None]*(length - len(param)))
            return Cvv(*param)
    
    def get_cv(self, is_full_cv: Optional[bool] = True) -> str:
        if is_full_cv:
            return self.cvv
        else:
            return self.cv if self.cv else self.cvv
        
    def get_lsd_c(self) -> str:
        return self.act_c if self.act_c is not None else self.c
    
    def get_lsd_v(self) -> str:
        return self.fol_v if self.fol_v is not None else self.v
        
    def get_lsd_cvv(self) -> tuple[str, str, str]:
        cvv = self.get_cv()
        c = self.get_lsd_c()
        v = self.get_lsd_v()
        return (cvv, c, v)

    def __str__(self) -> str:
        str_order = (self.cvv, self.cv, 
                     self.c, self.v, self.act_c, 
                     self.fol_v, self.mid_v, self.end_v)
        for value in str_order:
            if value:
                return str(value)
        else:
            return 'R'

    def __bool__(self) -> bool:
        for ele in self:
            if ele:
                return True
        else:
            return False
        

class RecLine(tuple[Cvv, ...]):
    def __new__(cls, *args):
        recline = (x for x in args)
        return super().__new__(cls, recline)

    def __str__(self, split_symbol: str = "_") -> str:
        if isinstance(self[0], Cvv):
            line: str = split_symbol + split_symbol.join(str(e) for e in self)
        else:
            line: str = split_symbol.join(str(e) for e in self)
        if "R" in line or line.islower():
            return line
        else:
            return f"{line}_UpperCase"
        
        
class Reclist(UserList[RecLine]):
    """a list of recline"""
    
    def __str__(self) -> str:
        line_str = []
        for line in self:
            line_str.append(str(line))
        return '\n'.join(line_str)