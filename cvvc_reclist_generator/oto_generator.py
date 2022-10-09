from ast import alias
from .data_struct import Alias, Cvv, Reclist, AliasType, AliasUnion, Oto, OtoUnion
from .errors import AliasTypeError


class OtoGenerator:
    """a oto generator"""

    def __init__(self) -> None:
        self.oto_union = OtoUnion()
        self.EMPTY_CVV = Cvv.new()

    def gen_oto(self, reclist: Reclist, alias_union: AliasUnion, bpm: float) -> None:
        """generate oto from reclist according to needed alias

        Args:
            reclist (Reclist): a reclist
            alias_union (AliasUnion): needed alias
            bpm (float): bpm of the recording BGM
        """

        for row in reclist:
            wav = f"{row}.wav"
            if len(row) == 3 and row[0] == row[1] == row[2]:
                if (
                    c_head := Alias(row[0].get_lsd_c(), AliasType.C_HEAD)
                ) in alias_union.c_head:
                    c_head_oto = self.get_oto(wav, c_head, 0, bpm)
                    self.oto_union.C.append(c_head_oto)
                    alias_union.c_head.discard(c_head)
                if (
                    cv_head := Alias(
                        row[0].get_cv(alias_union.is_full_cv), AliasType.CV_HEAD
                    )
                ) in alias_union.cv_head:
                    cv_head_oto = self.get_oto(wav, cv_head, 0, bpm)
                    self.oto_union.CV.append(cv_head_oto)
                    alias_union.cv_head.discard(cv_head)
                if (
                    cv := Alias(row[1].get_cv(alias_union.is_full_cv), AliasType.CV)
                ) in alias_union.cv:
                    cv_L = Alias(f"{cv}", AliasType.CV_LONG)
                    cv_oto = self.get_oto(wav, cv, 1, bpm)
                    cv_L_oto = self.get_oto(wav, cv_L, 2, bpm)
                    self.oto_union.CV.extend((cv_oto, cv_L_oto))
                    alias_union.cv.discard(cv)
                if (vc := Alias((row[0].v, row[1].c), AliasType.VC)) in alias_union.vc:
                    vc_oto = self.get_oto(wav, vc, 1, bpm)
                    self.oto_union.VC.append(vc_oto)
                    alias_union.vc.discard(vc)
                if (
                    vcv := Alias(
                        (row[0].v, row[1].get_cv(alias_union.is_full_cv)), AliasType.VCV
                    )
                ) in alias_union.vcv:
                    vcv_oto = self.get_oto(wav, vcv, 1, bpm)
                    self.oto_union.VCV.append(vcv_oto)
                    alias_union.vcv.discard(vcv)
                if (vr := Alias(row[2].v, AliasType.V)) in alias_union.v:
                    vr_oto = self.get_oto(wav, vr, 2, bpm)
                    self.oto_union.V.append(vr_oto)
                    alias_union.v.discard(vr)
            else:
                for idx, cvv in enumerate(row):
                    if idx == 0:
                        if (
                            c_head := Alias(cvv.get_lsd_c(), AliasType.C_HEAD)
                        ) in alias_union.c_head:
                            c_head_oto = self.get_oto(wav, c_head, idx, bpm)
                            self.oto_union.C.append(c_head_oto)
                            alias_union.c_head.discard(c_head)
                        cv_head = Alias(
                            cvv.get_cv(alias_union.is_full_cv), AliasType.CV_HEAD
                        )
                        if cv_head in alias_union.cv_head:
                            oto = self.get_oto(wav, cv_head, idx, bpm)
                            self.oto_union.CV.append(oto)
                            alias_union.cv_head.discard(cv_head)
                        if len(row) == 1 and (vr := Alias(cvv.v, AliasType.V)) in alias_union.v:
                            oto = self.get_oto(wav, vr, idx, bpm)
                            self.oto_union.V.append(oto)
                            alias_union.v.discard(vr)                            
                    else:
                        island: list[bool] = [False, False]
                        if idx < len(row) - 1 and row[idx + 1] == self.EMPTY_CVV:
                            if (vr := Alias(row[idx].v, AliasType.V)) in alias_union.v:
                                oto = self.get_oto(wav, vr, idx, bpm)
                                self.oto_union.V.append(oto)
                                alias_union.v.discard(vr)
                            island[1] = True
                        if idx <= len(row) - 1:
                            cv = Alias(cvv.get_cv(alias_union.is_full_cv), AliasType.CV)
                            cv_head = Alias(
                                cvv.get_cv(alias_union.is_full_cv), AliasType.CV_HEAD
                            )
                            if row[idx - 1] == self.EMPTY_CVV:
                                if cv_head in alias_union.cv_head:
                                    oto = self.get_oto(wav, cv_head, idx, bpm)
                                    self.oto_union.CV.append(oto)
                                    alias_union.cv_head.discard(cv_head)
                                island[0] = True
                            if any(island):
                                continue
                            if (
                                cv := Alias(
                                    cvv.get_cv(alias_union.is_full_cv), AliasType.CV
                                )
                            ) in alias_union.cv:
                                oto = self.get_oto(wav, cv, idx, bpm)
                                self.oto_union.CV.append(oto)
                                alias_union.cv.discard(cv)
                            if (
                                vc := Alias((row[idx - 1].v, cvv.c), AliasType.VC)
                            ) in alias_union.vc:
                                oto = self.get_oto(wav, vc, idx, bpm)
                                self.oto_union.VC.append(oto)
                                alias_union.vc.discard(vc)
                            if (
                                vcv := Alias(
                                    (
                                        row[idx - 1].v,
                                        cvv.get_cv(alias_union.is_full_cv),
                                    ),
                                    AliasType.VCV,
                                )
                            ) in alias_union.vcv:
                                oto = self.get_oto(wav, vcv, idx, bpm)
                                self.oto_union.VCV.append(oto)
                                alias_union.vcv.discard(vcv)
                        if (
                            idx == len(row) - 1
                            and (vr := Alias(row[idx].v, AliasType.V)) in alias_union.v
                        ):
                            oto = self.get_oto(wav, vr, idx, bpm)
                            self.oto_union.V.append(oto)
                            alias_union.v.discard(vr)

    def get_oto(
        self,
        wav: str,
        alias: Alias,
        position: int,
        bpm: float,
    ) -> Oto:
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
        bpm_param = float(bpm / 120)
        beat = bpm_param * (1250 + position * 500)
        OVL, CONSONANT_VEL, VOWEL_VEL = 80, 100, 200

        alias_type = alias._type

        if alias_type in (AliasType.C_HEAD, AliasType.C):
            offset = beat - 2 * CONSONANT_VEL
            consonant = beat - 0.25 * CONSONANT_VEL * bpm_param
            cutoff = -beat
            preutterance = beat - CONSONANT_VEL
            overlap = 10
        elif alias_type in (AliasType.CV, AliasType.CV_HEAD, AliasType.CV_LONG):
            offset = beat - CONSONANT_VEL
            consonant = 0.25 * 500 * bpm_param + CONSONANT_VEL
            cutoff = -(0.75 * 500 * bpm_param)
            preutterance = CONSONANT_VEL
            overlap = CONSONANT_VEL / 2
        elif alias_type == AliasType.V:
            offset = beat + 500 * bpm_param - OVL - VOWEL_VEL
            consonant = OVL + VOWEL_VEL + 100
            cutoff = -(consonant + 100)
            preutterance = OVL + VOWEL_VEL
            overlap = OVL
        elif alias_type == AliasType.VC:
            offset = beat - OVL - VOWEL_VEL - CONSONANT_VEL
            consonant = OVL + VOWEL_VEL + 0.33 * CONSONANT_VEL
            cutoff = -(OVL + VOWEL_VEL + CONSONANT_VEL)
            preutterance = OVL + VOWEL_VEL
            overlap = OVL
        elif alias_type == AliasType.VCV:
            offset = beat - OVL - VOWEL_VEL - CONSONANT_VEL
            consonant = OVL + VOWEL_VEL + CONSONANT_VEL + 0.25 * 500 * bpm_param
            cutoff = -(OVL + VOWEL_VEL + CONSONANT_VEL + 0.75 * 500 * bpm_param)
            preutterance = OVL + VOWEL_VEL + CONSONANT_VEL
            overlap = OVL
        else:
            raise AliasTypeError("Given type of alias is invalid.")

        oto = Oto(wav, alias, (offset, consonant, cutoff, preutterance, overlap))
        return oto

    def save_oto(self, oto_dir: str) -> None:
        """export oto.ini file.

        Args:
            oto_dir (str): the path of oto.ini file
        """
        with open(oto_dir, "w", encoding="utf-8") as f:
            f.write(str(self.oto_union))

    @staticmethod
    def export_oto(oto: OtoUnion, oto_path: str = "./result/oto.ini"):
        with open(oto_path, mode="w", encoding="shift-jis") as fp:
            fp.write(str(oto))
