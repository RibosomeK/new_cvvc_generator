from collections import UserList, namedtuple
from typing import Optional, Iterable
from cvv_workshop import CvvWorkshop
from alias import AliasUnion


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
    

class ReclistGenerator:
    """a reclist generator"""
    
    def __init__(self, dict_dir: str) -> None:
        self.cvv_workshop = CvvWorkshop()
        self.cvv_workshop.read_dict(dict_dir)
        self.reclist = Reclist()
        self.emptyCvv = Cvv.new()
        
    def gen_2mora(self, alias_union: AliasUnion) -> None:
        cv_list = list(alias_union.cv | alias_union.cv_head)
        cv_list.sort()
        for cv in cv_list:
            cvv = self.cvv_workshop.find_cvv(cvv=cv)
            if cvv:
                self.reclist.append(RecLine(cvv, cvv))
                alias_union.c_head.discard(cvv.get_lsd_c())
                alias_union.vc.discard((cvv.v, cvv.c))
                alias_union.vcv.discard((cvv.v, cvv.get_cv()))
                alias_union.vr.discard(cvv.v)
            else:
                print(f"{cv}= has no match word.")
                raise ValueError
            
        if alias_union.vcv:
            vcv_list = list(alias_union.vcv)
            vcv_list.sort()
            for vcv in vcv_list:
                v = Cvv.new()
                v._replace(v=vcv[0])
                cvv = self.cvv_workshop.find_cvv(cvv=vcv[1])
                self.reclist.append(RecLine((v, cvv)))
                alias_union.vc.discard((v.v, cvv.c))
                alias_union.vr.discard(cvv.v)
        vc_list = list(alias_union.vc)
        vc_list.sort()
        for vc in vc_list:
            v, c = Cvv.new(), Cvv.new()
            v._replace(v=vc[0]), c._replace(c=vc[1])
            self.reclist.append(RecLine((v, c)))
            
        if c_head_list := sorted(alias_union.c_head, reverse=True):
            row: list[Cvv] = []
            while c_head_list:
                c_head = c_head_list.pop()
                c_head = Cvv.new(('', '', '', c_head))
                if len(row) < 3:
                    row.extend([c_head, self.emptyCvv])
                else:
                    self.reclist.append(RecLine(*row))
                    row.clear()
            if row:
                self.reclist.append(RecLine(*row))
                
        if vr_list := sorted(alias_union.vr, reverse=True):
            row: list[Cvv] = []
            while vr_list:
                vr = vr_list.pop()
                vr = Cvv.new(('', '', vr))
                if len(row) < 3:
                    row.extend([vr, self.emptyCvv])
                else:
                    self.reclist.append(RecLine(*row))
                    row.clear()
            if row:
                self.reclist.append(RecLine(*row))

    def gen_plan_b(self, alias_union: AliasUnion) -> AliasUnion:
        all_cv = list(alias_union.cv | alias_union.cv_head)
        all_cv.sort()
        for cv in all_cv:
            if cv := self.cvv_workshop.find_cvv(cv):
                self.reclist.append(RecLine(cv, cv, cv))
                alias_union.c_head.discard(cv.get_lsd_c())
                alias_union.vc.discard((cv.v, cv.c))
                alias_union.vr.discard(cv.v)
                alias_union.vcv.discard((cv.v, cv.get_cv()))
            else:
                raise ValueError
        alias_union.cv.clear()
        alias_union.cv_head.clear()
        return alias_union

    def gen_mora_x(self, alias_union: AliasUnion, length: int, cv_mid: Optional[set[str]]=None) -> None:
        """Generate given x length long pre row of reclist.

        Args:
            alias_union (AliasUnion): Needed alias
            length (int): length pre row
            cv_mid (Optional[Set[str]], optional): 
                For some consonant is shorter in the beginning 
                that can be hard to oto like [y], [w] in mandarin. 
                Defaults to None.

        Returns: None
        """
        cv_mid = cv_mid if cv_mid else set()

        cv_list = sorted(alias_union.cv, reverse=True)
        while cv_list:
            row: list[Cvv] = []
            cv_mid_switch = False
            for i in range(length):
                if not cv_list:
                    break
                if cv_mid_switch:
                    continue
                cv = self.cvv_workshop.find_cvv(cvv=cv_list.pop())
                row.append(cv)
                if i == 0:
                    alias_union.c_head.discard(cv.get_lsd_c())
                    alias_union.cv_head.discard(cv.cvv)
                    alias_union.cv_head.discard(cv.cv)
                    if (cv.cvv in cv_mid) or (cv.cv in cv_mid):
                        row.append(cv)
                        cv_mid_switch = not cv_mid_switch
                elif i < length - 1:
                    alias_union.vc.discard((row[i-1].v, cv.c))
                    alias_union.vcv.discard((row[i-1].v, cv.get_cv()))
                else:
                    alias_union.vr.discard(cv.v)
            self.reclist.append(RecLine(*row))
        alias_union.cv.clear()
        
        # complete vcv part
        row: list[Cvv] = []
        i = 0
        while True:
            if not alias_union.vcv:
                break
            if i == 0:
                vcv = alias_union.vcv.pop(v=alias_union.vcv.max_v[0])
                v_cvv = self.cvv_workshop.find_cvv(v=vcv[0])
                cv_cvv = self.cvv_workshop.find_cvv(cvv=vcv[1])
                alias_union.vc.discard((v_cvv.v, cv_cvv.c))
                row = [v_cvv, cv_cvv]
                i += 2
            elif i <= length - 1:
                try:
                    vcv = alias_union.vcv.pop(v=row[-1].v)
                    next_cv = self.cvv_workshop.find_cvv(cvv=vcv[1])
                    alias_union.vc.discard((vcv[0], next_cv.c))
                    row.append(next_cv)
                    i += 1
                except ValueError:
                    if i <= length - 2:
                        vcv = alias_union.vcv.pop()
                        cv1 = self.cvv_workshop.find_cvv(v=vcv[0])
                        cv2 = self.cvv_workshop.find_cvv(cvv=vcv[1])
                        alias_union.vc.discard((row[-1].v, cv1.c))
                        alias_union.vc.discard((cv1.v, cv2.c))
                        row.extend([cv1, cv2])
                        i += 2
                    else:
                        i = length
                        continue
            elif i == length:
                self.reclist.append(RecLine(*row))
                alias_union.vr.discard(row[-1].v)
                alias_union.c_head.discard(row[0].get_lsd_c())
                alias_union.cv_head.discard(row[0].cvv)
                alias_union.cv_head.discard(row[0].cv)
                row: list[Cvv] = []
                i = 0
        if row:
            self.reclist.append(RecLine(*row))
            alias_union.vr.discard(row[-1].v)
            alias_union.c_head.discard(row[0].get_lsd_c())
            alias_union.cv_head.discard(row[0].cvv)
            alias_union.cv_head.discard(row[0].cv)

        # complete the vc part
        row: list[Cvv] = []
        i = 0
        while True:
            if not alias_union.vc:
                break
            if i == 0:
                current_v = alias_union.vc.max_v[0]
                current_cv = self.cvv_workshop.find_cvv(v=current_v)
                current_vc = alias_union.vc.pop(v=current_v)
                row.append(current_cv)
                row.append(self.cvv_workshop.find_next(current_vc, alias_union.vc.max_v[0]))
                i += 2
            elif i <= length - 1:
                try:
                    vc = alias_union.vc.pop(v=row[-1].v)
                    row.append(self.cvv_workshop.find_next(vc, alias_union.vc.max_v[0]))
                    i += 1
                except ValueError:
                    if i <= length - 2:
                        vc = alias_union.vc.pop()
                        cv1 = self.cvv_workshop.find_cvv(v=vc[0])
                        try:
                            cv2 = self.cvv_workshop.find_cvv(c=vc[1], v=alias_union.vc.max_v[0])
                        except ValueError:
                            cv2 = self.cvv_workshop.find_cvv(c=vc[1])
                        row.extend([cv1, cv2])
                        i += 2
                    else:
                        i = length
                        continue
            elif i == length:
                self.reclist.append(RecLine(*row))
                alias_union.vr.discard(row[-1].v)
                alias_union.c_head.discard(row[0].get_lsd_c())
                alias_union.cv_head.discard(row[0].cvv)
                alias_union.cv_head.discard(row[0].cv)
                row: list[Cvv] = []
                i = 0
        if row:
            self.reclist.append(RecLine(*row))
            alias_union.vr.discard(row[-1].v)
            alias_union.c_head.discard(row[0].get_lsd_c())
            alias_union.cv_head.discard(row[0].cvv)
            alias_union.cv_head.discard(row[0].cv)

        # complete cv head part
        cv_head_list = sorted(alias_union.cv_head, reverse=True)
        row: list[Cvv] = []
        while cv_head_list:
            for i in range(1 + length // 2):
                if not cv_head_list:
                    break
                row.append(self.cvv_workshop.find_cvv(cvv=cv_head_list.pop()))
                alias_union.vr.discard(row[-1].v)
                alias_union.c_head.discard(row[-1].get_lsd_c())
                row.append(self.emptyCvv)
            if row[-1] == self.emptyCvv:
                row.pop()
            self.reclist.append(RecLine(*row))
            row: list[Cvv] = []
        alias_union.cv_head.clear()

        # complete c head part
        c_head_list = list(sorted(alias_union.c_head, reverse=True))
        row: list[Cvv] = []
        while c_head_list:
            for i in range(1 + length // 2):
                if not c_head_list:
                    break
                c_head = c_head_list.pop()
                for cvv in self.cvv_workshop.cvv_set:
                    if cvv.get_lsd_c == c_head:
                        c_head = cvv
                        break
                else:
                    raise AttributeError
                row.extend((c_head, self.emptyCvv))
                alias_union.vr.discard(c_head.v)
            if row[-1] == self.emptyCvv:
                row.pop()
            self.reclist.append(RecLine(*row))
            row.clear()
        alias_union.c_head.clear()

        # complete ending v part
        vr_list = sorted(alias_union.vr, reverse=True)
        row: list[Cvv] = []
        while vr_list:
            for i in range(1 + length // 2):
                if not vr_list:
                    break
                row.append(self.cvv_workshop.find_cvv(v=vr_list.pop()))
                row.append(self.emptyCvv)
            if row[-1] == self.emptyCvv:
                row.pop()
            self.reclist.append(RecLine(*row))
            row: list[Cvv] = []
        alias_union.vr.clear()

    def save_reclist(self, reclist_dir: str) -> None:
        with open(reclist_dir, mode='w', encoding='utf-8') as f:
            f.write(str(self.reclist))
            