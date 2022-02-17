from ast import alias
from cvvc_generator_dataclasses import CVV, RecLine, OTO, VS_OTO, Alias_Type, AliasUnion, VC_Set
from collections import deque
from random import choice
from typing import List, Set, Dict, NamedTuple, Optional
import configparser

class CVVCReclistGenerator:
    def __init__(self) -> None:
        self.cvv: Set[CVV] = set()
        self.cvv_dict: Dict[str, CVV] = {}
        self.cv_dict: Dict[str, List[CVV]] = {}
        self.c_dict: Dict[str, List[CVV]] = {}
        self.v_dict: Dict[str, List[CVV]] = {}

        self.reclist: List[RecLine] = []
        self.oto: List[NamedTuple] = []
        
        self.vsdxmf: List[NamedTuple] = []
        self.redirect_vowel_dict: Dict[str, List[str]] = {}
        self.redirect_consonant_dict: Dict[str, List[str]] = {}
        self.redirect_cv_dict: Dict[str, List[str]] = {}

        self.alias: AliasUnion
        self.emptyCVV = CVV.new()

    def read_dict(self, dict_dir: str) -> None:
        """read a cvvc dict in the following format:
            bao,p,ao
            pao,ph,ao
            ...
            guang,k,uang
            kuang,kh,uang
        split symbol \t can also be used
        the format can be also extend for more detail structure of the word,
        more specific can be seen in OTO class

        Args:
            dict_dir (str): the path of dict file

        Raises:
            SyntaxError: more than 8 elements are given

        [Todo]:
            comment support, both multipul lines and single
        """
        with open(dict_dir, mode="r", encoding="utf-8") as dict_file:
            dict_content = dict_file.read()

        for line in dict_content.splitlines():
            if line:
                if "," in line:
                    split_symbol = ','
                elif "\t" in line:
                    split_symbol = '\t'
                else:
                    raise SyntaxError
                word = CVV.new(line.split(split_symbol))
                cvv, c, v, *_ = word
                self.cvv.add(word)
                self.cvv_dict.setdefault(cvv, word)
                if word.cv:
                    self.cv_dict.setdefault(word.cv, []).append(word)
                self.c_dict.setdefault(c, []).append(word)
                self.v_dict.setdefault(v, []).append(word)

    def find_cvv(
        self,
        cvv: str = None,
        c: str = None,
        v: str = None,
        exception: Optional[Set[str]] = None,
    ) -> CVV:
        """find a cvv class by a cvv, c, or v

        Returns:
            [CVV]: [description]
        """
        if cvv:
            if cv := self.cvv_dict.get(cvv):
                return cv
            else:
                if cv_list := self.cv_dict.get(cvv):
                    return choice(cv_list)
                else:
                    raise ValueError
        if c and not v:
            if cvv_list := self.c_dict.get(c):
                if exception:
                    new_cvv_list: List[CVV] = []
                    for cv in cvv_list:
                        if cv.v not in exception:
                            new_cvv_list.append(cv)
                    cvv_list = new_cvv_list
                if not cvv_list:
                    raise ValueError
                return choice(cvv_list)
        if v and not c:
            if cvv_list := self.v_dict.get(v):
                if exception:
                    new_cvv_list: List[CVV] = []
                    for cv in cvv_list:
                        if cv.c not in exception:
                            new_cvv_list.append(cv)
                    cvv_list = new_cvv_list
                if not cvv_list:
                    raise ValueError
                return choice(cvv_list)
        if c and v:
            if cvv_list := self.c_dict.get(c):
                for cv in cvv_list:
                    if cv.v == v:
                        return cv
                else:
                    raise ValueError
        raise SyntaxError

    def get_needed_alias(
        self,
        is_c_head: bool = False,
        is_cv_head: bool = True,
        is_full_cv: bool = True,
        alias_config: Optional[str] = None,
    ) -> AliasUnion:
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
        if not is_full_cv:
            for cvv in self.cvv:
                if cvv.cv is not None:
                    self.redirect_cv_dict.setdefault(cvv.cv, []).append(cvv.cvv)
        alias_union = AliasUnion()
        if is_c_head:
            alias_union.c_head = {x.get_lsd_c() for x in self.cvv}
        alias_union.cv = {cv.get_cv(is_full_cv) for cv in self.cvv}
        if is_cv_head:
            alias_union.cv_head = alias_union.cv.copy()
        alias_union.vc = VC_Set()
        alias_union.vc.update(
            (v, c) 
            for v in self.v_dict
            for c in self.c_dict
        )
        alias_union.vr = {v for v in self.v_dict}
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
            if key == "_cv" or key == "cv":
                for cv in value.split(","):
                    if self.find_cvv(cvv=cv):
                        unneeded.__dict__[cv].add(cv)
                    elif cv in self.c_dict:
                        unneeded.__dict__[cv].update(
                            cvv.get_cv(is_full_cv) for cvv in self.c_dict[cv]
                        )
                    else:
                        raise ValueError
            elif key == "vc":
                for vc in value.split(","):
                    if vc in self.c_dict:
                        unneeded.vc.update((v, vc) for v in self.v_dict)
                    if vc in self.v_dict:
                        unneeded.vc.update((vc, c) for c in self.c_dict)
                    elif " " in vc:
                        unneeded.vc.add(tuple(vc.split(" ")))
                    else:
                        raise ValueError
            elif key == "vr":
                unneeded.vr.update(value.split(","))
            elif key == "_c":
                unneeded.c_head.update(value.split(","))
            elif key == "vcv":
                for vcv in value.split(","):
                    if vcv in self.c_dict:
                        unneeded.vcv.update(
                            (v, cvv.get_cv())
                            for v in self.v_dict
                            for cvv in self.c_dict[vcv]
                        )
                    elif vcv in self.v_dict:
                        unneeded.vcv.update(
                            (vcv, cvv.get_cv()) 
                            for cvv in self.cvv
                        )
                    elif " " in vcv:
                        unneeded.vcv.add(tuple(vcv.split(" ")))
        vcv_value = config["NEEDED"]["vcv"]
        if vcv_value.upper() == "ALL":
            needed.vcv.update(
                (v, cvv.get_cv()) 
                for v in self.v_dict
                for cvv in self.cvv
            )
        elif "," in vcv_value:
            for vcv in vcv_value.split(","):
                if vcv in self.c_dict:
                    needed.vcv.update(
                        (v, cvv.get_cv())
                        for v in self.v_dict
                        for cvv in self.c_dict[vcv]
                    )
                elif vcv in self.v_dict:
                    needed.vcv.update(
                        (vcv, cvv.get_cv()) 
                        for cvv in self.cvv
                    )
                elif " " in vcv:
                    needed.vcv.add(tuple(vcv.split(" ")))
        return unneeded, needed

    def gen_2mora(self, alias_union: AliasUnion) -> None:
        cv_list = list(alias_union.cv | alias_union.cv_head)
        cv_list.sort()
        for cv in cv_list:
            cvv = self.find_cvv(cvv=cv)
            if cvv:
                self.reclist.append(RecLine(cvv, cvv))
                alias_union.vc.discard((cvv.v, cvv.c))
                if alias_union.vcv:
                    alias_union.vcv.discard((cvv.v, cvv.get_cv()))
                alias_union.vr.discard(cvv.v)
            else:
                print(f"{cv}= has no match word.")
                raise ValueError
        if alias_union.vcv:
            vcv_list = list(alias_union.vcv)
            vcv_list.sort()
            for vcv in vcv_list:
                v = CVV.new()
                v._replace(v=vcv[0])
                cvv = self.find_cvv(cvv=vcv[1])
                self.reclist.append(RecLine((v, cvv)))
                alias_union.vc.discard((v.v, cvv.c))
                alias_union.vr.discard(cvv.v)
        vc_list = list(alias_union.vc)
        vc_list.sort()
        for vc in vc_list:
            v, c = CVV.new(), CVV.new()
            v._replace(v=vc[0]), c._replace(c=vc[1])
            self.reclist.append(RecLine((v, c)))
        if vr_deque := deque(sorted(list(alias_union.vr))):
            row: List[CVV] = []
            while vr_deque:
                vr = vr_deque.popleft()
                vr = CVV(None, None, vr, None, None, None, None, None)
                if len(row) < 3:
                    row.extend([vr, self.emptyCVV])
                else:
                    self.reclist.append(RecLine(*row))
                    row.clear()
            if row:
                self.reclist.append(RecLine(*row))

    def gen_plan_b(self, alias_union: AliasUnion) -> AliasUnion:
        all_cv = list(alias_union.cv | alias_union.cv_head)
        all_cv.sort()
        for cv in all_cv:
            if cv := self.find_cvv(cv):
                self.reclist.append(RecLine(cv, cv, cv))
                alias_union.vc.discard((cv.v, cv.c))
                alias_union.vr.discard(cv.v)
                if alias_union.vcv:
                    alias_union.vcv.discard((cv.v, cv.get_cv()))
            else:
                raise ValueError
        alias_union.cv.clear()
        alias_union.cv_head.clear()
        return alias_union

    def gen_mora_x(
        self, 
        alias_union: AliasUnion, 
        length: int, 
        cv_mid: Optional[Set[str]] = None
    ) -> None:
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

        cv_deque = deque(sorted(list(alias_union.cv)))
        while cv_deque:
            row: List[CVV] = []
            cv_mid_switch = False
            for i in range(length):
                if not cv_deque:
                    break
                if cv_mid_switch:
                    continue
                cv = self.find_cvv(cvv=cv_deque.popleft())
                row.append(cv)
                if i == 0:
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
        row: List[CVV] = []
        i = 0
        while True:
            if not alias_union.vcv:
                break
            if i == 0:
                vcv = alias_union.vcv.pop(v=alias_union.vcv.max_v[0])
                v_cvv = self.find_cvv(v=vcv[0])
                cv_cvv = self.find_cvv(cvv=vcv[1])
                alias_union.vc.discard((v_cvv.v, cv_cvv.c))
                row = [v_cvv, cv_cvv]
                i += 2
            elif i <= length - 1:
                try:
                    vcv = alias_union.vcv.pop(v=row[-1].v)
                    next_cv = self.find_cvv(cvv=vcv[1])
                    alias_union.vc.discard((vcv[0], next_cv.c))
                    row.append(next_cv)
                    i += 1
                except ValueError:
                    if i <= length - 2:
                        vcv = alias_union.vcv.pop()
                        cv1 = self.find_cvv(v=vcv[0])
                        cv2 = self.find_cvv(cvv=vcv[1])
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
                alias_union.cv_head.discard(row[0].cvv)
                alias_union.cv_head.discard(row[0].cv)
                row: List[CVV] = []
                i = 0
        if row:
            self.reclist.append(RecLine(*row))
            alias_union.vr.discard(row[-1].v)
            alias_union.cv_head.discard(row[0].cvv)
            alias_union.cv_head.discard(row[0].cv)

        # complete the vc part
        def find_next(vc: tuple[str, str], vc_max_v: str) -> CVV:
            try:
                next_cv = self.find_cvv(c=vc[1], v=vc_max_v)
            except ValueError:
                next_cv = self.find_cvv(c=vc[1])
            return next_cv

        row: List[CVV] = []
        i = 0
        while True:
            if not alias_union.vc:
                break
            if i == 0:
                current_v = alias_union.vc.max_v[0]
                current_cv = self.find_cvv(v=current_v)
                current_vc = alias_union.vc.pop(v=current_v)
                row.append(current_cv)
                row.append(find_next(current_vc, alias_union.vc.max_v[0]))
                i += 2
            elif i <= length - 1:
                try:
                    vc = alias_union.vc.pop(v=row[-1].v)
                    row.append(find_next(vc, alias_union.vc.max_v[0]))
                    i += 1
                except ValueError:
                    if i <= length - 2:
                        vc = alias_union.vc.pop()
                        cv1 = self.find_cvv(v=vc[0])
                        try:
                            cv2 = self.find_cvv(c=vc[1], v=alias_union.vc.max_v[0])
                        except ValueError:
                            cv2 = self.find_cvv(c=vc[1])
                        row.extend([cv1, cv2])
                        i += 2
                    else:
                        i = length
                        continue
            elif i == length:
                self.reclist.append(RecLine(*row))
                alias_union.vr.discard(row[-1].v)
                alias_union.cv_head.discard(row[0].cvv)
                alias_union.cv_head.discard(row[0].cv)
                row: List[CVV] = []
                i = 0
        if row:
            self.reclist.append(RecLine(*row))
            alias_union.vr.discard(row[-1].v)
            alias_union.cv_head.discard(row[0].cvv)
            alias_union.cv_head.discard(row[0].cv)

        # complete cv head part
        _cv_dq = deque(sorted(list(alias_union.cv_head)))
        row: List[CVV] = []
        while _cv_dq:
            for i in range(1 + length // 2):
                if not _cv_dq:
                    break
                row.append(self.find_cvv(cvv=_cv_dq.popleft()))
                alias_union.vr.discard(row[-1].v)
                row.append(self.emptyCVV)
            if row[-1] == self.emptyCVV:
                row.pop()
            self.reclist.append(RecLine(*row))
            row: List[CVV] = []
        alias_union.cv_head.clear()

        # complete ending v part
        vr_dq = deque(sorted(list(alias_union.vr)))
        row: List[CVV] = []
        while vr_dq:
            for i in range(1 + length // 2):
                if not vr_dq:
                    break
                row.append(self.find_cvv(v=vr_dq.popleft()))
                row.append(self.emptyCVV)
            if row[-1] == self.emptyCVV:
                row.pop()
            self.reclist.append(RecLine(*row))
            row: List[CVV] = []
        alias_union.vr.clear()
        
    def gen_oto(self, alias_union: AliasUnion, bpm: float, is_full_cv: bool = True, cv_mid: Set[str]=None):
        """Generate all otos.

        Args:
            alias_union (AliasUnion): [description]
        """
        cv_mid = cv_mid if cv_mid else set()
        cv_oto_list: List[OTO] = []
        vc_oto_list: List[OTO] = []
        vcv_oto_list: List[OTO] = []
        vr_oto_list: List[OTO] = []
        for row in self.reclist:
            wav = f'{row}.wav'
            if len(row) == 3 and row[0] == row[1] == row[2]:
                if (_cv := row[0].get_cv(is_full_cv)) in alias_union.cv_head:
                    _cv_alias = f'- {row[0].get_cv(is_full_cv)}'
                    _cv_oto = self.get_oto(Alias_Type.CV, wav, _cv_alias, 0, bpm)
                    cv_oto_list.append(_cv_oto)
                    alias_union.cv_head.discard(_cv)
                if (cv := row[1].get_cv(is_full_cv)) in alias_union.cv:
                    cv_alias = row[1].get_cv(is_full_cv)
                    cv_L_alias = f'{row[2].get_cv(is_full_cv)}_L'
                    cv_oto = self.get_oto(Alias_Type.CV, wav, cv_alias, 1, bpm)
                    cv_L_oto = self.get_oto(Alias_Type.CV, wav, cv_L_alias, 2, bpm)
                    cv_oto_list.extend((cv_oto, cv_L_oto))
                    alias_union.cv.discard(cv)
                if (vc := (row[0].v, row[1].c)) in alias_union.vc:
                    vc_oto = self.get_oto(Alias_Type.VC, wav, vc, 1, bpm)
                    vc_oto_list.append(vc_oto)
                    alias_union.vc.discard(vc)
                if (vcv := (row[0].v, row[1].get_cv())) in alias_union.vcv:
                    vcv_oto = self.get_oto(Alias_Type.VCV, wav, vcv, 1, bpm)
                    vcv_oto_list.append(vcv_oto)
                    alias_union.vcv.discard(vcv)
                if (vr := row[2].v) in alias_union.vr:
                    vr_alias = f'{row[2].v} R'
                    vr_oto = self.get_oto(Alias_Type.VR, wav, vr_alias, 2, bpm)
                    vr_oto_list.append(vr_oto)
                    alias_union.vr.discard(vr)
            else:
                for idx, cvv in enumerate(row):
                    if idx == 0:
                        cv = cvv.get_cv(is_full_cv)
                        if cv in alias_union.cv_head:
                            _cv_alias = f'- {cv}'
                            oto = self.get_oto(Alias_Type.CV, wav, _cv_alias, idx, bpm)
                            cv_oto_list.append(oto)
                            alias_union.cv_head.discard(cv)
                        if cv in alias_union.cv and cv not in cv_mid:
                            oto = self.get_oto(Alias_Type.CV, wav, cv, idx, bpm)
                            cv_oto_list.append(oto)
                            alias_union.cv_head.discard(cv)
                    elif idx <= len(row)-1:
                        if (cv := cvv.get_cv(is_full_cv)) in alias_union.cv:
                            oto = self.get_oto(Alias_Type.CV, wav, cv, idx, bpm)
                            cv_oto_list.append(oto)
                            alias_union.cv_head.discard(cv)
                        if (vc := (row[idx-1].v, cvv.c)) in alias_union.vc:
                            oto = self.get_oto(Alias_Type.VC, wav, vc, idx, bpm)
                            vc_oto_list.append(oto)
                            alias_union.vc.discard(vc)
                        if (vcv := (row[idx-1].v, cvv.get_cv())) in alias_union.vcv:
                            oto = self.get_oto(Alias_Type.VCV, wav, vcv, idx, bpm)
                            vcv_oto_list.append(oto)
                            alias_union.vcv.discard(vcv)
                    if idx == len(row)-1 and (vr := row[idx].v) in alias_union.vr:
                        vr_alias = f'{vr} R'
                        oto = self.get_oto(Alias_Type.VR, wav, vr_alias, idx, bpm)
                        vr_oto_list.append(oto)
                        alias_union.vr.discard(vr)
        self.oto.extend(cv_oto_list)
        self.oto.extend(vc_oto_list)
        self.oto.extend(vcv_oto_list)
        self.oto.extend(vr_oto_list)
        
    def check_lsd_cvv_uniqueness(self) -> None:
        check_dict: Dict[tuple[str, str], List[str]] = {}
        for cvv in self.cvv:
            cv, c, v = cvv.get_lsd_cvv()
            check_dict.setdefault((c, v), []).append(cv)
        for key, value in check_dict.items():
            if len(value) > 1:
                print(f'Following cv have the same attribute of c and v ({key}):')
                print(','.join(value))
        
    def read_redirect_config(self, redirect_config_dir) -> None:
        redirect_config = configparser.ConfigParser(allow_no_value=True)
        redirect_config.read(redirect_config_dir, encoding='utf-8')
        self.redirect_vowel_dict = {
            key: values.split(',') 
            for key, values in redirect_config["VOWEL"].items()
            }
        self.redirect_consonant_dict = {
            key: values.split(',')
            for key, values in redirect_config['CONSONANT'].items()
        }
                        
    def gen_vsdxmf(
        self, 
        alias_union: AliasUnion, 
        bpm: float, 
        is_full_cv: bool = False, 
        cv_mid: Set[str]=None, 
        redirect_config_dir: Optional[str]=None
    ) -> None:
        """Generate vsdxmf for vocalsharp.

        Args:
            alias_union (AliasUnion): [description]
            bpm (float): [description]
            is_full_cv (bool, optional): [description]. Defaults to False.
            cv_mid (Set[str], optional): [description]. Defaults to None.
            redirect_config_dir (Optional[str], optional): [description]. Defaults to None.
        """
        cv_mid = cv_mid if cv_mid else set()
        if redirect_config_dir:
            self.read_redirect_config(redirect_config_dir)
                
        c_vsdxmf_list: List[VS_OTO] = []
        cv_vsdxmf_list: List[VS_OTO] = []
        vc_vsdxmf_list: List[VS_OTO] = []
        vr_vsdxmf_list: List[VS_OTO] = []
        
        for row in self.reclist:
            wav = f'{row}.wav'
            if row[0] == row[1] == row[2]:
                if (c := row[0].c) in alias_union.c_head:
                    c_vsdxmf = self.get_vs_oto(Alias_Type.C, wav, c, 0, bpm)
                    c_vsdxmf_list.extend(c_vsdxmf)
                    alias_union.c_head.discard(c)
                if (cv := row[1].get_cv(is_full_cv)) in alias_union.cv and row[0].c != row[0].v:
                    cv_alias = row[1].get_cv(is_full_cv)
                    cv_vsdxmf = self.get_vs_oto(Alias_Type.CV, wav, cv_alias, 1, bpm)
                    cv_L_vsdxmf = self.get_vs_oto(Alias_Type.CV, wav, cv_alias, 2, bpm)
                    for L_vsdxmf in cv_L_vsdxmf:
                        L_vsdxmf = L_vsdxmf._replace(phoneme=f'{L_vsdxmf.phoneme}_L')
                        cv_vsdxmf_list.append(L_vsdxmf)
                    cv_vsdxmf_list.extend(cv_vsdxmf)
                    alias_union.cv.discard(cv)
                if (vc := (row[0].v, row[1].c)) in alias_union.vc:
                    vc_vsdxmf = self.get_vs_oto(Alias_Type.VC, wav, vc, 1, bpm)
                    vc_vsdxmf_list.extend(vc_vsdxmf)
                    alias_union.vc.discard(vc)
                '''if (vcv := (row[0].v, row[1].get_cv())) in alias.vcv:
                    vcv_vsdxmf = self.get_vs_oto(Alias_Type.VCV, wav, vcv, 1, bpm)
                    vcv_vsdxmf_list.append(vcv_vsdxmf)
                    alias.vcv.discard(vcv)'''
                if (vr := row[2].v) in alias_union.vr:
                    vr_vsdxmf = self.get_vs_oto(Alias_Type.VR, wav, vr, 2, bpm)
                    vr_vsdxmf_list.extend(vr_vsdxmf)
                    alias_union.vr.discard(vr)
            else:
                for idx, cvv in enumerate(row):
                    if idx == 0:
                        if (c := cvv.c) in alias_union.c_head:
                            vsdxmf = self.get_vs_oto(Alias_Type.C, wav, c, idx, bpm)
                            c_vsdxmf_list.extend(vsdxmf)
                            alias_union.c_head.discard(c)
                        cv = cvv.get_cv(is_full_cv)
                        if cv in alias_union.cv and cv not in cv_mid and cvv.c != cvv.v:
                            vsdxmf = self.get_vs_oto(Alias_Type.CV, wav, cv, idx, bpm)
                            cv_vsdxmf_list.extend(vsdxmf)
                            alias_union.cv_head.discard(cv)
                    elif idx <= len(row)-1:
                        if (cv := cvv.get_cv(is_full_cv)) in alias_union.cv and cvv.c != cvv.v:
                            vsdxmf = self.get_vs_oto(Alias_Type.CV, wav, cv, idx, bpm)
                            cv_vsdxmf_list.extend(vsdxmf)
                            alias_union.cv_head.discard(cv)
                        if (vc := (row[idx-1].v, cvv.c)) in alias_union.vc:
                            vsdxmf = self.get_vs_oto(Alias_Type.VC, wav, vc, idx, bpm)
                            vc_vsdxmf_list.extend(vsdxmf)
                            alias_union.vc.discard(vc)
                        '''if (vcv := (row[idx-1].v, cvv.get_cv())) in alias.vcv:
                            vsdxmf = self.get_vs_oto(Alias_Type.VCV, wav, vcv, idx, bpm)
                            vcv_vsdxmf_list.append(vsdxmf)
                            alias.vcv.discard(vcv)'''
                    if idx == len(row)-1 and (vr := row[idx].v) in alias_union.vr:
                        vsdxmf = self.get_vs_oto(Alias_Type.VR, wav, vr, idx, bpm)
                        vr_vsdxmf_list.extend(vsdxmf)
                        alias_union.vr.discard(vr)
                        
        self.vsdxmf.extend(c_vsdxmf_list)
        self.vsdxmf.extend(cv_vsdxmf_list)
        self.vsdxmf.extend(vc_vsdxmf_list)
        self.vsdxmf.extend(vr_vsdxmf_list)
            
        
    def get_oto(
        self, 
        alias_type: Alias_Type, 
        wav: str,
        alias: str | tuple[str, str], 
        position: int,
        bpm: float
    ) -> OTO:
        """Get one single oto.

        Args:
            alias_type (str): the type of alias: [cv, vc, vcv, vr]
            wav (str) : the string of wav
            alias (str or tuple[str, str]): alias in oto, tuple for vc and vcv types
            position (int): position in row, start from 0. for vc and vcv types use the c or cv position
            bpm (float): the bpm of recording BGM

        Returns:
            OTO the class
        """
        bpm_param = float(120 / bpm)
        beat = bpm_param*(1250 + position*500)
        OVL, CONSONANT_VEL, VOWEL_VEL = 80, 100, 200
            
        if alias_type == Alias_Type.CV:
            offset = beat - CONSONANT_VEL
            consonant = 0.25*500*bpm_param + CONSONANT_VEL
            cutoff = -(beat + 0.75*500*bpm_param)
            preutterance = CONSONANT_VEL
            overlap = CONSONANT_VEL / 2
        elif alias_type == Alias_Type.VR:
            offset = beat + 500*bpm_param - OVL - VOWEL_VEL
            consonant = OVL + VOWEL_VEL + 100
            cutoff = -(consonant + 100)
            preutterance = OVL + VOWEL_VEL
            overlap = OVL
        elif alias_type == Alias_Type.VC:
            alias = '{} {}'.format(*alias)
            offset = beat - OVL - VOWEL_VEL - CONSONANT_VEL
            consonant = OVL + VOWEL_VEL + 0.33*CONSONANT_VEL
            cutoff = -(OVL + VOWEL_VEL + CONSONANT_VEL)
            preutterance = OVL + VOWEL_VEL
            overlap = OVL
        elif alias_type == Alias_Type.VCV:
            alias = '{} {}'.format(*alias)
            offset = beat - OVL - VOWEL_VEL - CONSONANT_VEL
            consonant = OVL + VOWEL_VEL + CONSONANT_VEL + 0.25*500*bpm_param
            cutoff = -(OVL + VOWEL_VEL + CONSONANT_VEL + 0.75*500*bpm_param)
            preutterance = OVL + VOWEL_VEL + CONSONANT_VEL
            overlap = OVL
        else:
            raise TypeError
            
        oto = OTO(wav, None, alias, None, offset, consonant, cutoff, preutterance, overlap)
        return oto
    
    def get_redirect_phoneme(self, phoneme: str | tuple[str, str], alias_type: Alias_Type) -> List[str]:
        redirect_phoneme: List[str] = []
        if alias_type == Alias_Type.C:
            if phoneme in self.v_dict:
                redirect_consonant_dict = self.redirect_vowel_dict
            else:
                redirect_consonant_dict = self.redirect_consonant_dict
            if phoneme in redirect_consonant_dict:
                for redirect_consonant in redirect_consonant_dict.get(str(phoneme), []):
                    redirect_phoneme.append(f' {redirect_consonant}')
                    
        elif alias_type == Alias_Type.CV:
            if phoneme in self.redirect_cv_dict:
                for cv in self.redirect_cv_dict.get(str(phoneme), []):
                    _, c, v = self.find_cvv(cvv=cv).get_lsd_cvv()
                    redirect_phoneme.append(f'{c} {v}')
                    
        elif alias_type == Alias_Type.VC:
            v, c = phoneme
            if c in self.v_dict:
                redirect_consonant_dict = self.redirect_vowel_dict
            else:
                redirect_consonant_dict = self.redirect_consonant_dict
                
            if v in self.redirect_vowel_dict:
                for redirect_vowel in self.redirect_vowel_dict[v]:
                    redirect_phoneme.append(f'{redirect_vowel} {c}')
                    
            if c in redirect_consonant_dict:
                for redirect_consonant in redirect_consonant_dict[c]:
                    redirect_phoneme.append(f'{v} {redirect_consonant}')
                    
            if v in self.redirect_vowel_dict and c in redirect_consonant_dict:
                for redirect_vowel in self.redirect_vowel_dict[v]:
                    for redirect_consonant in redirect_consonant_dict[c]:
                        redirect_phoneme.append(f'{redirect_vowel} {redirect_consonant}')
                        
        elif alias_type == Alias_Type.VR:
            for redirect_vowel in self.redirect_vowel_dict.get(str(phoneme), []):
                redirect_phoneme.append(f'{redirect_vowel} ')
                
        else:
            raise TypeError('Given wrong alias type!')
        
        return redirect_phoneme
    
    def get_vs_oto(
        self,
        alias_type: Alias_Type, 
        wav: str,
        alias: str | tuple[str, str], 
        position: int,
        bpm: float, 
    ) -> List[VS_OTO]:
        bpm_param = float(120 / bpm)
        beat = bpm_param*(1250 + position*500)
        OVL, CONSONANT_VEL, VOWEL_VEL = 80, 100, 200
        vs_oto_list: List[VS_OTO] = []
            
        if alias_type == Alias_Type.C:
            phoneme = f' {alias}'
            offset = beat - 20 - CONSONANT_VEL
            preutterance = offset + 20
            consonant = preutterance + 0.25*CONSONANT_VEL
            cutoff = consonant + CONSONANT_VEL
            overlap = offset + 5
        elif alias_type == Alias_Type.CV:
            cvv = self.find_cvv(cvv=str(alias))
            phoneme = f'{cvv.get_lsd_c()} {cvv.get_lsd_v()}'
            offset = beat - CONSONANT_VEL
            preutterance = beat
            consonant = 0.25*500*bpm_param + preutterance
            cutoff = consonant + 0.75*500*bpm_param
            overlap = offset + CONSONANT_VEL / 2
        elif alias_type == Alias_Type.VR:
            phoneme = f'{alias} '
            offset = beat + 500*bpm_param - OVL - VOWEL_VEL
            preutterance = offset + OVL + VOWEL_VEL
            consonant = preutterance + 100
            cutoff = consonant + 100
            overlap = offset + OVL
        elif alias_type == Alias_Type.VC:
            phoneme = '{} {}'.format(*alias)
            offset = beat - OVL - VOWEL_VEL - CONSONANT_VEL
            preutterance = beat - CONSONANT_VEL
            consonant = preutterance + 0.33*CONSONANT_VEL
            cutoff = beat
            overlap = offset + OVL
            '''
        elif alias_type == Alias_Type.VCV:
            alias = '{} {}'.format(*alias)
            offset = beat - OVL - VOWEL_VEL - CONSONANT_VEL
            preutterance = beat
            consonant = beat + 0.25*500*bpm_param
            cutoff = beat + 0.75*500*bpm_param
            overlap = offset + OVL
            '''
        else:
            raise TypeError
        vs_oto = VS_OTO(phoneme, wav, offset, preutterance, consonant, cutoff, overlap)
        vs_oto_list.append(vs_oto)

        redirect_phoneme_list = self.get_redirect_phoneme(alias, alias_type)
        for _redirect_phoneme in redirect_phoneme_list:
            vs_oto_list.append(VS_OTO.get_redirect(_redirect_phoneme, vs_oto.phoneme))
        
        return vs_oto_list

    def save_reclist(self, reclist_dir: str) -> None:
        with open(reclist_dir, mode="w", encoding="utf-8") as reclist_file:
            reclist_str = "\n".join(str(row) for row in self.reclist)
            reclist_file.write(reclist_str)

    def save_oto(self, oto_dir: str) -> None:
        with open(oto_dir, mode="w", encoding="utf-8") as oto_file:
            oto_str = "\n".join(str(oto) for oto in self.oto)
            oto_file.write(oto_str)
            
    def save_presamp(self, presamp_dir: str) -> None:
        presamp_ini: List[str] = ['[VERSION]\n'
                                  '1.7']
        presamp_ini.append('[VOWEL]')
        for v, cvv_list in self.v_dict.items():
            v_str = ','.join(str(cvv) for cvv in cvv_list)
            v_str = f'{v}={v}={v_str}=100'
            presamp_ini.append(v_str)
        presamp_ini.append('[CONSONANT]')
        for c, cvv_list in self.c_dict.items():
            if c in self.v_dict:
                continue
            c_str = ','.join(str(cvv) for cvv in cvv_list)
            c_str = f'{c}={c_str}=1'
            presamp_ini.append(c_str)
        presamp_ini.append('[ENDTYPE]\n'
                           '%v% R\n'
                           '[ENDFLAG]\n'
                           '1')
        with open(presamp_dir, mode='w', encoding='utf-8') as f:
            f.write('\n'.join(presamp_ini))
            
    def save_vsdxmf(self, vsdxmf_dir: str) -> None:
        with open(vsdxmf_dir, mode='w', encoding='utf-8') as f:
            vsdxmf_str = '\n'.join(str(vsdxmf) for vsdxmf in self.vsdxmf)
            f.write(vsdxmf_str)
            
    def check_integrity(self, alias_union: AliasUnion) -> None:
        # _c_log = self.check_c_head_integrity()
        cv_head_log = self.check_cv_head_integrity(alias_union.cv_head)
        cv_log = self.check_cv_integrity(alias_union.cv)
        vcv_log = self.check_vcv_integrity(alias_union.vcv)
        vc_log = self.check_vc_integrity(alias_union.vc)
        vr_log = self.check_vr_integrity(alias_union.vr)
        print(f'Missing cv head: {cv_head_log}\n'
              f'Missing cv: {cv_log}\n'
              f'Missing vcv: {vcv_log}\n'
              f'Missing vc: {vc_log}\n'
              f'Missing ending v: {vr_log}')
        
    def check_cv_head_integrity(self, cv_set: Set[str]) -> str:
        for row in self.reclist:
            cv_set.discard(row[0].cvv)
            cv_set.discard(row[0].cv)
            if self.emptyCVV in row:
                for cvv in row:
                    if cvv != self.emptyCVV:
                        cv_set.discard(cvv.cvv)
                        cv_set.discard(cvv.cv)
        _cv_log = ', '.join(cv_set) if cv_set else 'None'
        return _cv_log
    
    def check_cv_integrity(self, cv_set: Set[str], cv_mid: Optional[Set[str]]=None) -> str:
        cv_mid = cv_mid if cv_mid else set()
        for row in self.reclist:
            for idx, cvv in enumerate(row):
                if idx == 0 and (cvv.cv in cv_mid or cvv.cvv in cv_mid):
                    continue
                cv_set.discard(cvv.cvv)
                cv_set.discard(cvv.cv)
        cv_log = ', '.join(cv_set) if cv_set else 'None'
        return cv_log
    
    def check_vc_integrity(self, vc_set: Set[tuple[str, str]]) -> str:
        for row in self.reclist:
            for idx, cvv in enumerate(row):
                if idx == 0:
                    continue
                vc_set.discard((row[idx-1].v, cvv.c))
        vc_log = ", ".join(str(vc) for vc in vc_set) if vc_set else 'None'
        return vc_log
    
    def check_vcv_integrity(self, vcv_set: Set[tuple[str, str]]) -> str:
        for row in self.reclist:
            for idx, cvv in enumerate(row):
                if idx == 0:
                    continue
                vcv_set.discard((row[idx-1].v, cvv.get_cv()))
        vcv_log = ", ".join(str(vcv) for vcv in vcv_set) if vcv_set else 'None'
        return vcv_log
            
    def check_vr_integrity(self, vr_set: Set[str]) -> str:
        for row in self.reclist:
            vr_set.discard(row[-1].v)
        vr_log = ', '.join(vr_set) if vr_set else 'None'
        return vr_log
