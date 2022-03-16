from .cvv_dataclasses import Reclist, AliasType, AliasUnion, Oto, OtoUnion
from typing import Iterable, Optional
from .errors import AliasTypeError


class OtoGenerator:
    """a oto generator"""
    
    def __init__(self) -> None:
        self.oto_union = OtoUnion()
    
    def gen_oto(self, reclist: Reclist, alias_union: AliasUnion, bpm: float, is_full_cv: bool = True, cv_mid: Optional[Iterable[str]]=None) -> None:
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
                    c_head_oto = self._get_oto(AliasType.C, wav, c_head_alias, 0, bpm)
                    self.oto_union[AliasType.C].append(c_head_oto)
                    alias_union.c_head.discard(c_head)
                if (cv_head := row[0].get_cv(is_full_cv)) in alias_union.cv_head:
                    cv_head_alias = f'- {cv_head}'
                    cv_head_oto = self._get_oto(AliasType.CV, wav, cv_head_alias, 0, bpm)
                    self.oto_union[AliasType.CV].append(cv_head_oto)
                    alias_union.cv_head.discard(cv_head)
                if (cv := row[1].get_cv(is_full_cv)) in alias_union.cv:
                    cv_L_alias = f'{cv}_L'
                    cv_oto = self._get_oto(AliasType.CV, wav, cv, 1, bpm)
                    cv_L_oto = self._get_oto(AliasType.CV, wav, cv_L_alias, 2, bpm)
                    self.oto_union[AliasType.CV].extend((cv_oto, cv_L_oto))
                    alias_union.cv.discard(cv)
                if (vc := (row[0].v, row[1].c)) in alias_union.vc:
                    vc_oto = self._get_oto(AliasType.VC, wav, vc, 1, bpm)
                    self.oto_union[AliasType.VC].append(vc_oto)
                    alias_union.vc.discard(vc)
                if (vcv := (row[0].v, row[1].get_cv())) in alias_union.vcv:
                    vcv_oto = self._get_oto(AliasType.VCV, wav, vcv, 1, bpm)
                    self.oto_union[AliasType.VCV].append(vcv_oto)
                    alias_union.vcv.discard(vcv)
                if (vr := row[2].v) in alias_union.vr:
                    vr_alias = f'{vr} R'
                    vr_oto = self._get_oto(AliasType.V, wav, vr_alias, 2, bpm)
                    self.oto_union[AliasType.V].append(vr_oto)
                    alias_union.vr.discard(vr)
            else:
                for idx, cvv in enumerate(row):
                    if idx == 0:
                        if (c_head := cvv.get_lsd_c()) in alias_union.c_head:
                            c_head_alias = f'- {c_head}'
                            c_head_oto = self._get_oto(AliasType.C, wav, c_head_alias, idx, bpm)
                            self.oto_union[AliasType.C].append(c_head_oto)
                        cv = cvv.get_cv(is_full_cv)
                        if cv in alias_union.cv_head:
                            cv_head_alias = f'- {cv}'
                            oto = self._get_oto(AliasType.CV, wav, cv_head_alias, idx, bpm)
                            self.oto_union[AliasType.CV].append(oto)
                            alias_union.cv_head.discard(cv)
                        if cv in alias_union.cv and cv not in cv_mid:
                            oto = self._get_oto(AliasType.CV, wav, cv, idx, bpm)
                            self.oto_union[AliasType.CV].append(oto)
                            alias_union.cv_head.discard(cv)
                    elif idx <= len(row)-1:
                        if (cv := cvv.get_cv(is_full_cv)) in alias_union.cv:
                            oto = self._get_oto(AliasType.CV, wav, cv, idx, bpm)
                            self.oto_union[AliasType.CV].append(oto)
                            alias_union.cv_head.discard(cv)
                        if (vc := (row[idx-1].v, cvv.c)) in alias_union.vc:
                            oto = self._get_oto(AliasType.VC, wav, vc, idx, bpm)
                            self.oto_union[AliasType.VC].append(oto)
                            alias_union.vc.discard(vc)
                        if (vcv := (row[idx-1].v, cvv.get_cv())) in alias_union.vcv:
                            oto = self._get_oto(AliasType.VCV, wav, vcv, idx, bpm)
                            self.oto_union[AliasType.VCV].append(oto)
                            alias_union.vcv.discard(vcv)
                    if idx == len(row)-1 and (vr := row[idx].v) in alias_union.vr:
                        vr_alias = f'{vr} R'
                        oto = self._get_oto(AliasType.V, wav, vr_alias, idx, bpm)
                        self.oto_union[AliasType.V].append(oto)
                        alias_union.vr.discard(vr)
        alias_union = alias_union_backup.copy()
                        
    def _get_oto(self, alias_type: AliasType, wav: str, alias: str | tuple[str, str], position: int, bpm: float) -> Oto:
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
        elif alias_type == AliasType.V:
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
            raise AliasTypeError('Given type of alias is invalid.')
            
        oto = Oto(wav, None, alias, None, offset, consonant, cutoff, preutterance, overlap)
        return oto
    
    def save_oto(self, oto_dir: str) -> None:
        """export oto.ini file.

        Args:
            oto_dir (str): the path of oto.ini file
        """
        with open(oto_dir, 'w', encoding='utf-8') as f:
            f.write(str(self.oto_union))
            