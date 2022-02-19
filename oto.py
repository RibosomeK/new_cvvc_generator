from collections import UserDict, namedtuple
from alias import AliasType, AliasUnion
from reclist import Reclist


class Oto(namedtuple("OTO", "wav prefix alias suffix l con r pre ovl")):
    """single line of oto"""
    __slot__ = ()

    def __str__(self) -> str:
        alias = self.alias
        if self.prefix:
            alias = self.prefix + self.alias
        if self.suffix:
            alias += self.suffix
        return "{}={},{},{},{},{},{}".format(self.wav, alias, *self[-5:])
    

class OtoUnion(UserDict):
    """a set of otos"""
    
    __is_frozen: bool = True
    
    @property
    def _is_frozen(self) -> bool:
        return self.__is_frozen
    
    @_is_frozen.setter
    def _is_freeze(self, value) -> None:
        self.__is_frozen = value
    
    def __new__(cls: type[UserDict]) -> UserDict:
        oto_union = UserDict()
        oto_union[AliasType.C] = [list[Oto]]
        oto_union[AliasType.CV] = [list[Oto]]
        oto_union[AliasType.VC] = [list[Oto]]
        oto_union[AliasType.VCV] = [list[Oto]]
        oto_union[AliasType.VR] = [list[Oto]]
        return oto_union
        
    def __setitem__(self, key: ..., item: ...) -> None:
        if self.__is_frozen and key not in self:
            raise ValueError("can't add new keys")
        return super().__setitem__(key, item)
    
    def __str__(self) -> str:
        oto_str = []
        for section in self.__dict__:
            for oto in section:
                oto_str.append(str(oto))
        return '\n'.join(oto_str)


class OtoGenerator:
    """a oto generator"""
    
    def __init__(self) -> None:
        self.oto_union = OtoUnion()
    
    def gen_oto(self, reclist: Reclist, alias_union: AliasUnion, bpm: float, is_full_cv: bool = True, cv_mid: set[str]=None) -> None:
        """generate oto from reclist according to needed alias

        Args:
            reclist (Reclist): a reclist
            alias_union (AliasUnion): needed alias
            bpm (float): bpm of the recording BGM
            is_full_cv (bool, optional): wheather use full cv in oto. Defaults to True.
            cv_mid (set[str], optional): wheather to use beginning cv as a middle cv. Defaults to None.
        """
        alias_union_backup = alias_union.copy()
        cv_mid = cv_mid if cv_mid else set()
        for row in reclist:
            wav = f'{row}.wav'
            if len(row) == 3 and row[0] == row[1] == row[2]:
                if (c_head := row[0].get_lsd_c()) in alias_union.c_head:
                    c_head_alias = f'- {c_head}'
                    c_head_oto = self.get_oto(AliasType.C, wav, c_head_alias, 0, bpm)
                    self.oto_union[AliasType.C].append(c_head_oto)
                    alias_union.c_head.discard(c_head)
                if (cv_head := row[0].get_cv(is_full_cv)) in alias_union.cv_head:
                    cv_head_alias = f'- {cv_head}'
                    cv_head_oto = self.get_oto(AliasType.CV, wav, cv_head_alias, 0, bpm)
                    self.oto_union[AliasType.CV].append(cv_head_oto)
                    alias_union.cv_head.discard(cv_head)
                if (cv := row[1].get_cv(is_full_cv)) in alias_union.cv:
                    cv_L_alias = f'{cv}_L'
                    cv_oto = self.get_oto(AliasType.CV, wav, cv, 1, bpm)
                    cv_L_oto = self.get_oto(AliasType.CV, wav, cv_L_alias, 2, bpm)
                    self.oto_union[AliasType.CV].extend((cv_oto, cv_L_oto))
                    alias_union.cv.discard(cv)
                if (vc := (row[0].v, row[1].c)) in alias_union.vc:
                    vc_oto = self.get_oto(AliasType.VC, wav, vc, 1, bpm)
                    self.oto_union[AliasType.VC].append(vc_oto)
                    alias_union.vc.discard(vc)
                if (vcv := (row[0].v, row[1].get_cv())) in alias_union.vcv:
                    vcv_oto = self.get_oto(AliasType.VCV, wav, vcv, 1, bpm)
                    self.oto_union[AliasType.VCV].append(vcv_oto)
                    alias_union.vcv.discard(vcv)
                if (vr := row[2].v) in alias_union.vr:
                    vr_alias = f'{vr} R'
                    vr_oto = self.get_oto(AliasType.VR, wav, vr_alias, 2, bpm)
                    self.oto_union[AliasType.VR].append(vr_oto)
                    alias_union.vr.discard(vr)
            else:
                for idx, cvv in enumerate(row):
                    if idx == 0:
                        if (c_head := cvv.get_lsd_c()) in alias_union.c_head:
                            c_head_alias = f'- {c_head}'
                            c_head_oto = self.get_oto(AliasType.C, wav, c_head_alias, idx, bpm)
                            self.oto_union[AliasType.C].append(c_head_oto)
                        cv = cvv.get_cv(is_full_cv)
                        if cv in alias_union.cv_head:
                            cv_head_alias = f'- {cv}'
                            oto = self.get_oto(AliasType.CV, wav, cv_head_alias, idx, bpm)
                            self.oto_union[AliasType.CV].append(oto)
                            alias_union.cv_head.discard(cv)
                        if cv in alias_union.cv and cv not in cv_mid:
                            oto = self.get_oto(AliasType.CV, wav, cv, idx, bpm)
                            self.oto_union[AliasType.CV].append(oto)
                            alias_union.cv_head.discard(cv)
                    elif idx <= len(row)-1:
                        if (cv := cvv.get_cv(is_full_cv)) in alias_union.cv:
                            oto = self.get_oto(AliasType.CV, wav, cv, idx, bpm)
                            self.oto_union[AliasType.CV].append(oto)
                            alias_union.cv_head.discard(cv)
                        if (vc := (row[idx-1].v, cvv.c)) in alias_union.vc:
                            oto = self.get_oto(AliasType.VC, wav, vc, idx, bpm)
                            self.oto_union[AliasType.VC].append(oto)
                            alias_union.vc.discard(vc)
                        if (vcv := (row[idx-1].v, cvv.get_cv())) in alias_union.vcv:
                            oto = self.get_oto(AliasType.VCV, wav, vcv, idx, bpm)
                            self.oto_union[AliasType.VCV].append(oto)
                            alias_union.vcv.discard(vcv)
                    if idx == len(row)-1 and (vr := row[idx].v) in alias_union.vr:
                        vr_alias = f'{vr} R'
                        oto = self.get_oto(AliasType.VR, wav, vr_alias, idx, bpm)
                        self.oto_union[AliasType.VR].append(oto)
                        alias_union.vr.discard(vr)
        alias_union = alias_union_backup.copy()
                        
    def get_oto(self, alias_type: AliasType, wav: str, alias: str | tuple[str, str], position: int, bpm: float) -> Oto:
        """Get one single oto.

        Args:
            alias_type (str): the type of alias: [cv, vc, vcv, vr]
            wav (str) : the string of wav
            alias (str or tuple[str, str]): alias in oto, tuple for vc and vcv types
            position (int): position in row, start from 0. for vc and vcv types use the c or cv position
            bpm (float): the bpm of recording BGM

        Returns:
            a single line of oto
        """
        bpm_param = float(120 / bpm)
        beat = bpm_param*(1250 + position*500)
        OVL, CONSONANT_VEL, VOWEL_VEL = 80, 100, 200
            
        if alias_type == AliasType.C:
            offset = beat - 2*CONSONANT_VEL
            consonant = beat - 0.25*CONSONANT_VEL*bpm_param
            cutoff = - beat
            preutterance = beat - CONSONANT_VEL
            overlap = 10    
        elif alias_type == AliasType.CV:
            offset = beat - CONSONANT_VEL
            consonant = 0.25*500*bpm_param + CONSONANT_VEL
            cutoff = -(beat + 0.75*500*bpm_param)
            preutterance = CONSONANT_VEL
            overlap = CONSONANT_VEL / 2
        elif alias_type == AliasType.VR:
            offset = beat + 500*bpm_param - OVL - VOWEL_VEL
            consonant = OVL + VOWEL_VEL + 100
            cutoff = -(consonant + 100)
            preutterance = OVL + VOWEL_VEL
            overlap = OVL
        elif alias_type == AliasType.VC:
            alias = '{} {}'.format(*alias)
            offset = beat - OVL - VOWEL_VEL - CONSONANT_VEL
            consonant = OVL + VOWEL_VEL + 0.33*CONSONANT_VEL
            cutoff = -(OVL + VOWEL_VEL + CONSONANT_VEL)
            preutterance = OVL + VOWEL_VEL
            overlap = OVL
        elif alias_type == AliasType.VCV:
            alias = '{} {}'.format(*alias)
            offset = beat - OVL - VOWEL_VEL - CONSONANT_VEL
            consonant = OVL + VOWEL_VEL + CONSONANT_VEL + 0.25*500*bpm_param
            cutoff = -(OVL + VOWEL_VEL + CONSONANT_VEL + 0.75*500*bpm_param)
            preutterance = OVL + VOWEL_VEL + CONSONANT_VEL
            overlap = OVL
        else:
            raise TypeError
            
        oto = Oto(wav, None, alias, None, offset, consonant, cutoff, preutterance, overlap)
        return oto
    
    def save_oto(self, oto_dir: str) -> None:
        """export oto.ini file.

        Args:
            oto_dir (str): the path of oto.ini file
        """
        with open(oto_dir, 'w', encoding='utf-8') as f:
            f.write(str(self.oto_union))