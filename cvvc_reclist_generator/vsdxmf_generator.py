from cvvc_reclist_generator.errors import AliasTypeError
from .data_struct import (
    Cvv,
    Reclist,
    AliasType,
    Alias,
    AliasUnion,
    Vsdxmf,
    VsdxmfUnion,
    CvvWorkshop,
)


class VsdxmfGenerator:
    """a vsdxmf generator"""

    def __init__(self, cvv_workshop: CvvWorkshop) -> None:
        self.vsdxmf_union = VsdxmfUnion()
        self.cvv_workshop = cvv_workshop
        self.EMPTY = Cvv.new()

    def gen_vsdxmf(self, reclist: Reclist, alias_union: AliasUnion, bpm: float) -> None:
        for row in reclist:
            wav = f"{row}.wav"
            if len(row) == 3 and row[0] == row[1] == row[2]:
                if (
                    c := Alias(row[0].get_lsd_c(), AliasType.C_HEAD)
                ) in alias_union.c_head:
                    c_vsdxmf = self.get_vsdxmf(
                        ("", c.alias[0], AliasType.C_HEAD), wav, 0, bpm
                    )
                    self.vsdxmf_union.C.extend(c_vsdxmf)
                    alias_union.c_head.discard(c)
                if (
                    cv := Alias(row[1].get_cv(alias_union.is_full_cv), AliasType.CV)
                ) in alias_union.cv and row[0].c != row[0].v:
                    cv_alias = row[1].get_lsd_c(), row[-1].get_lsd_v()
                    cv_vsdxmf = self.get_vsdxmf((*cv_alias, AliasType.CV), wav, 1, bpm)
                    cv_L_vsdxmf = self.get_vsdxmf(
                        (*cv_alias, AliasType.CV_LONG), wav, 2, bpm
                    )
                    self.vsdxmf_union.CV.extend(cv_L_vsdxmf)
                    self.vsdxmf_union.CV.extend(cv_vsdxmf)
                    alias_union.cv.discard(cv)
                if (vc := Alias((row[0].v, row[1].c), AliasType.VC)) in alias_union.vc:
                    vc_vsdxmf = self.get_vsdxmf((*vc.alias, AliasType.VC), wav, 1, bpm)
                    self.vsdxmf_union.VC.extend(vc_vsdxmf)
                    alias_union.vc.discard(vc)
                """if (vcv := (row[0].v, row[1].get_cv())) in alias.vcv:
                    vcv_vsdxmf = self.get_vs_oto(Alias_Type.VCV, wav, vcv, 1, bpm)
                    vcv_vsdxmf_list.append(vcv_vsdxmf)
                    alias.vcv.discard(vcv)"""
                if (vr := Alias(row[2].v, AliasType.V)) in alias_union.v:
                    vr_vsdxmf = self.get_vsdxmf(
                        (vr.alias[0], "", AliasType.V), wav, 2, bpm
                    )
                    self.vsdxmf_union.V.extend(vr_vsdxmf)
                    alias_union.v.discard(vr)
            else:
                for idx, cvv in enumerate(row):
                    if idx == 0:
                        # c_head
                        if cvv.c != cvv.v and cvv.c not in self.cvv_workshop.v_dict:
                            c_head = Alias(cvv.get_lsd_c(), AliasType.C_HEAD)
                            if c_head in alias_union.c_head:
                                c_head_vsdxmf = self.get_vsdxmf(
                                    ("", cvv.get_lsd_c(), AliasType.C_HEAD),
                                    wav,
                                    idx,
                                    bpm,
                                )
                                self.vsdxmf_union.C.extend(c_head_vsdxmf)
                                alias_union.c_head.discard(c_head)
                        # v_head
                        elif cvv.c == cvv.v:
                            v_head = Alias(
                                cvv.get_cv(alias_union.is_full_cv), AliasType.CV_HEAD
                            )
                            if v_head in alias_union.cv_head:
                                v_head_vsdxmf = self.get_vsdxmf(
                                    ("", cvv.get_lsd_c(), AliasType.C_HEAD),
                                    wav,
                                    idx,
                                    bpm,
                                )
                                self.vsdxmf_union.C.extend(v_head_vsdxmf)
                                alias_union.cv_head.discard(v_head)
                    else:
                        if cvv == self.EMPTY:
                            # v
                            vr = Alias(row[idx - 1].v, AliasType.V)
                            if vr in alias_union.v:
                                vr_vsdxmf = self.get_vsdxmf(
                                    (row[idx - 1].v, "", AliasType.V),
                                    wav,
                                    idx - 1,
                                    bpm,
                                )
                                self.vsdxmf_union.V.extend(vr_vsdxmf)
                                alias_union.v.discard(vr)
                            continue
                        if row[idx - 1] == self.EMPTY:
                            # c_head
                            if cvv.c != cvv.v and cvv.c not in self.cvv_workshop.v_dict:
                                c_head = Alias(cvv.get_lsd_c(), AliasType.C_HEAD)
                                if c_head in alias_union.c_head:
                                    c_head_vsdxmf = self.get_vsdxmf(
                                        ("", cvv.get_lsd_c(), AliasType.C_HEAD),
                                        wav,
                                        idx,
                                        bpm,
                                    )
                                    self.vsdxmf_union.C.extend(c_head_vsdxmf)
                                    alias_union.c_head.discard(c_head)
                            # v_head
                            elif cvv.c == cvv.v:
                                v_head = Alias(
                                    cvv.get_cv(alias_union.is_full_cv),
                                    AliasType.CV_HEAD,
                                )
                                if v_head in alias_union.cv_head:
                                    v_head_vsdxmf = self.get_vsdxmf(
                                        ("", cvv.get_lsd_c(), AliasType.C_HEAD),
                                        wav,
                                        idx,
                                        bpm,
                                    )
                                    self.vsdxmf_union.C.extend(v_head_vsdxmf)
                                    alias_union.cv_head.discard(v_head)
                        else:
                            # cv
                            # vc
                            vc = Alias((row[idx - 1].v, cvv.c), AliasType.VC)
                            if vc in alias_union.vc:
                                vc_vsdxmf = self.get_vsdxmf(
                                    (
                                        row[idx - 1].v,
                                        cvv.c,
                                        AliasType.VC,
                                    ),
                                    wav,
                                    idx,
                                    bpm,
                                )
                                self.vsdxmf_union.VC.extend(vc_vsdxmf)
                                alias_union.vc.discard(vc)
                            if cvv.c != cvv.v:
                                cv = Alias(
                                    cvv.get_cv(alias_union.is_full_cv), AliasType.CV
                                )
                                if cv in alias_union.cv:
                                    cv_vsdxmf = self.get_vsdxmf(
                                        (
                                            cvv.get_lsd_c(),
                                            cvv.get_lsd_v(),
                                            AliasType.CV,
                                        ),
                                        wav,
                                        idx,
                                        bpm,
                                    )
                                    self.vsdxmf_union.CV.extend(cv_vsdxmf)
                                    alias_union.cv.discard(cv)
                    if idx == len(row) - 1:
                        # v
                        with open("debug.txt", mode="a") as fp:
                            fp.write(f"{wav}\n")
                        vr = Alias(cvv.v, AliasType.V)
                        if vr in alias_union.v:
                            vr_vsdxmf = self.get_vsdxmf(
                                (cvv.v, "", AliasType.V),
                                wav,
                                idx,
                                bpm,
                            )
                            self.vsdxmf_union.V.extend(vr_vsdxmf)
                            alias_union.v.discard(vr)

    def get_vsdxmf(
        self,
        phoneme: tuple[str, str, AliasType],
        wav: str,
        position: int,
        bpm: float,
    ) -> list[Vsdxmf]:
        bpm_param = float(120 / bpm)
        beat = bpm_param * (1250 + position * 500)
        OVL, CONSONANT_VEL, VOWEL_VEL = 80, 100, 200
        vsdxmf_list: list[Vsdxmf] = []

        alias_type = phoneme[-1]
        if alias_type == AliasType.C_HEAD:
            offset = beat - 20 - CONSONANT_VEL
            preutterance = offset + 20
            consonant = preutterance + 0.25 * CONSONANT_VEL
            cutoff = consonant + CONSONANT_VEL
            overlap = offset + 5
        elif alias_type in (AliasType.CV, AliasType.CV_LONG):
            offset = beat - CONSONANT_VEL
            preutterance = beat
            consonant = 0.25 * 500 * bpm_param + preutterance
            cutoff = consonant + 0.75 * 500 * bpm_param
            overlap = offset + CONSONANT_VEL / 2
        elif alias_type == AliasType.V:
            offset = beat + 500 * bpm_param - OVL - VOWEL_VEL
            preutterance = offset + OVL + VOWEL_VEL
            consonant = preutterance + 100
            cutoff = consonant + 100
            overlap = offset + OVL
        elif alias_type == AliasType.VC:
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

        vsdxmf = Vsdxmf(
            phoneme, wav, (offset, preutterance, consonant, cutoff, overlap)
        )
        vsdxmf_list.append(vsdxmf)

        redirect_phoneme_list = self.cvv_workshop.get_redirect_phoneme(phoneme)
        for redirect_phoneme in redirect_phoneme_list:
            vsdxmf_list.append(
                Vsdxmf.get_redirect(redirect_phoneme, str(vsdxmf).split(",")[0])
            )

        return vsdxmf_list

    def save_vsdxmf(self, vsdxmf_dir: str) -> None:
        with open(vsdxmf_dir, mode="w", encoding="utf-8") as f:
            f.write(str(self.vsdxmf_union))
