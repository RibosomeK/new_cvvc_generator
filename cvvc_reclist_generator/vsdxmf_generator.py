from cvvc_reclist_generator.errors import AliasTypeError
from .cvv_dataclasses import (
    Reclist,
    AliasType,
    Vsdxmf,
    VsdxmfUnion,
    CvvWorkshop,
)
from .alias_union import AliasUnion


class VsdxmfGenerator:
    """a vsdxmf generator"""

    def __init__(self, cvv_workshop: CvvWorkshop) -> None:
        self.vsdxmf_union = VsdxmfUnion()
        self.cvv_workshop = cvv_workshop

    def gen_vsdxmf(self, reclist: Reclist, alias_union: AliasUnion, bpm: float) -> None:
        """Generate vsdxmf for vocalsharp.

        Args:
            alias_union (AliasUnion): [description]
            bpm (float): [description]
            is_full_cv (bool, optional): [description]. Defaults to False.
            cv_mid (Set[str], optional): [description]. Defaults to None.
        """

        for row in reclist:
            wav = f"{row}.wav"
            if len(row) == 3 and row[0] == row[1] == row[2]:
                if (c := row[0].get_lsd_c()) in alias_union.c_head:
                    c_vsdxmf = self._get_vs_oto(AliasType.C, wav, c, 0, bpm)
                    self.vsdxmf_union[AliasType.C].extend(c_vsdxmf)
                    alias_union.c_head.discard(c)
                if (
                    cv := row[1].get_cv(alias_union.is_full_cv)
                ) in alias_union.cv and row[0].c != row[0].v:
                    cv_alias = row[1].get_cv(alias_union.is_full_cv)
                    cv_vsdxmf = self._get_vs_oto(AliasType.CV, wav, cv_alias, 1, bpm)
                    cv_L_vsdxmf = self._get_vs_oto(AliasType.CV, wav, cv_alias, 2, bpm)
                    for L_vsdxmf in cv_L_vsdxmf:
                        L_vsdxmf.phoneme = f"{L_vsdxmf.phoneme}_L"
                        self.vsdxmf_union[AliasType.CV].append(L_vsdxmf)
                    self.vsdxmf_union[AliasType.CV].extend(cv_vsdxmf)
                    alias_union.cv.discard(cv)
                if (vc := (row[0].v, row[1].c)) in alias_union.vc:
                    vc_vsdxmf = self._get_vs_oto(AliasType.VC, wav, vc, 1, bpm)
                    self.vsdxmf_union[AliasType.VC].extend(vc_vsdxmf)
                    alias_union.vc.discard(vc)
                """if (vcv := (row[0].v, row[1].get_cv())) in alias.vcv:
                    vcv_vsdxmf = self.get_vs_oto(Alias_Type.VCV, wav, vcv, 1, bpm)
                    vcv_vsdxmf_list.append(vcv_vsdxmf)
                    alias.vcv.discard(vcv)"""
                if (vr := row[2].v) in alias_union.vr:
                    vr_vsdxmf = self._get_vs_oto(AliasType.V, wav, vr, 2, bpm)
                    self.vsdxmf_union[AliasType.V].extend(vr_vsdxmf)
                    alias_union.vr.discard(vr)
            else:
                for idx, cvv in enumerate(row):
                    if idx == 0:
                        if (c := cvv.get_lsd_c()) in alias_union.c_head:
                            vsdxmf = self._get_vs_oto(AliasType.C, wav, c, idx, bpm)
                            self.vsdxmf_union[AliasType.C].extend(vsdxmf)
                            alias_union.c_head.discard(c)
                        cv = cvv.get_cv(alias_union.is_full_cv)
                        if (
                            cv in alias_union.cv
                            and cv not in alias_union.cv_mid
                            and cvv.c != cvv.v
                        ):
                            vsdxmf = self._get_vs_oto(AliasType.CV, wav, cv, idx, bpm)
                            self.vsdxmf_union[AliasType.CV].extend(vsdxmf)
                            alias_union.cv_head.discard(cv)
                    elif idx <= len(row) - 1:
                        if (
                            cv := cvv.get_cv(alias_union.is_full_cv)
                        ) in alias_union.cv and cvv.c != cvv.v:
                            vsdxmf = self._get_vs_oto(AliasType.CV, wav, cv, idx, bpm)
                            self.vsdxmf_union[AliasType.CV].extend(vsdxmf)
                            alias_union.cv_head.discard(cv)
                        if (vc := (row[idx - 1].v, cvv.c)) in alias_union.vc:
                            vsdxmf = self._get_vs_oto(AliasType.VC, wav, vc, idx, bpm)
                            self.vsdxmf_union[AliasType.VC].extend(vsdxmf)
                            alias_union.vc.discard(vc)
                        """if (vcv := (row[idx-1].v, cvv.get_cv())) in alias.vcv:
                            vsdxmf = self.get_vs_oto(Alias_Type.VCV, wav, vcv, idx, bpm)
                            vcv_vsdxmf_list.append(vsdxmf)
                            alias.vcv.discard(vcv)"""
                    if idx == len(row) - 1 and (vr := row[idx].v) in alias_union.vr:
                        vsdxmf = self._get_vs_oto(AliasType.V, wav, vr, idx, bpm)
                        self.vsdxmf_union[AliasType.V].extend(vsdxmf)
                        alias_union.vr.discard(vr)

    def _get_vs_oto(
        self,
        alias_type: AliasType,
        wav: str,
        alias: str | tuple[str, str],
        position: int,
        bpm: float,
    ) -> list[Vsdxmf]:
        bpm_param = float(120 / bpm)
        beat = bpm_param * (1250 + position * 500)
        OVL, CONSONANT_VEL, VOWEL_VEL = 80, 100, 200
        vsdxmf_list: list[Vsdxmf] = []

        if alias_type == AliasType.C:
            phoneme = f" {alias}"
            offset = beat - 20 - CONSONANT_VEL
            preutterance = offset + 20
            consonant = preutterance + 0.25 * CONSONANT_VEL
            cutoff = consonant + CONSONANT_VEL
            overlap = offset + 5
        elif alias_type == AliasType.CV:
            cvv = self.cvv_workshop.find_cvv(cvv=str(alias))
            phoneme = f"{cvv.get_lsd_c()} {cvv.get_lsd_v()}"
            offset = beat - CONSONANT_VEL
            preutterance = beat
            consonant = 0.25 * 500 * bpm_param + preutterance
            cutoff = consonant + 0.75 * 500 * bpm_param
            overlap = offset + CONSONANT_VEL / 2
        elif alias_type == AliasType.V:
            phoneme = f"{alias} "
            offset = beat + 500 * bpm_param - OVL - VOWEL_VEL
            preutterance = offset + OVL + VOWEL_VEL
            consonant = preutterance + 100
            cutoff = consonant + 100
            overlap = offset + OVL
        elif alias_type == AliasType.VC:
            phoneme = "{} {}".format(*alias)
            offset = beat - OVL - VOWEL_VEL - CONSONANT_VEL
            preutterance = beat - CONSONANT_VEL
            consonant = preutterance + 0.33 * CONSONANT_VEL
            cutoff = beat
            overlap = offset + OVL
            """
        elif alias_type == Alias_Type.VCV:
            alias = '{} {}'.format(*alias)
            offset = beat - OVL - VOWEL_VEL - CONSONANT_VEL
            preutterance = beat
            consonant = beat + 0.25*500*bpm_param
            cutoff = beat + 0.75*500*bpm_param
            overlap = offset + OVL
            """
        else:
            raise AliasTypeError
        vsdxmf = Vsdxmf(phoneme, wav, offset, preutterance, consonant, cutoff, overlap)
        vsdxmf_list.append(vsdxmf)

        redirect_phoneme_list = self.cvv_workshop.get_redirect_phoneme(
            alias, alias_type
        )
        for redirect_phoneme in redirect_phoneme_list:
            vsdxmf_list.append(Vsdxmf.get_redirect(redirect_phoneme, vsdxmf.phoneme))

        return vsdxmf_list

    def save_vsdxmf(self, vsdxmf_dir: str) -> None:
        with open(vsdxmf_dir, mode="w", encoding="utf-8") as f:
            f.write(str(self.vsdxmf_union))
