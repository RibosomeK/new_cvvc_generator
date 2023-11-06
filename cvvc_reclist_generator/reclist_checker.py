from cvvc_reclist_generator.data_struct import Cvv, Reclist, AliasUnion, VcSet


class ReclistChecker:
    """a checker to check integrity"""

    def __init__(self, reclist: Reclist, alias_union: AliasUnion) -> None:
        self.reclist = reclist
        self.alias_union = alias_union
        self.emptyCvv = Cvv.new()

    def check(self):
        c_head_log = self.check_c_head_integrity(self.alias_union.c_head)
        cv_head_log = self.check_cv_head_integrity(self.alias_union.cv_head)
        cv_log = self.check_cv_integrity(self.alias_union.cv)
        vcv_log = self.check_vcv_integrity(self.alias_union.vcv)
        vc_log = self.check_vc_integrity(self.alias_union.vc)
        vr_log = self.check_vr_integrity(self.alias_union.v)
        print(
            f"Missing c head: {c_head_log}\n"
            f"Missing cv head: {cv_head_log}\n"
            f"Missing cv: {cv_log}\n"
            f"Missing vcv: {vcv_log}\n"
            f"Missing vc: {vc_log}\n"
            f"Missing ending v: {vr_log}"
        )

    def check_c_head_integrity(self, c_set: set[str]) -> str:
        for row in self.reclist:
            c_set.discard(row[0].get_lsd_c())
            if self.emptyCvv in row:
                for cvv in row:
                    if cvv != self.emptyCvv:
                        c_set.discard(cvv.get_lsd_c())
        c_log = ", ".join(c_set) if c_set else "None"
        return c_log

    def check_cv_head_integrity(self, cv_set: set[str]) -> str:
        for row in self.reclist:
            cv_set.discard(row[0].cvv)
            cv_set.discard(row[0].cv)
            if self.emptyCvv in row:
                for cvv in row:
                    if cvv != self.emptyCvv:
                        cv_set.discard(cvv.cvv)
                        cv_set.discard(cvv.cv)
        cv_head_log = ", ".join(cv_set) if cv_set else "None"
        return cv_head_log

    def check_cv_integrity(self, cv_set: set[str]) -> str:
        for row in self.reclist:
            for idx, cvv in enumerate(row):
                if idx == 0 and (
                    cvv.cv in self.alias_union.cv_mid
                    or cvv.cvv in self.alias_union.cv_mid
                ):
                    continue
                cv_set.discard(cvv.cvv)
                cv_set.discard(cvv.cv)
        cv_log = ", ".join(cv_set) if cv_set else "None"
        return cv_log

    def check_vc_integrity(self, vc_set: VcSet) -> str:
        for row in self.reclist:
            for idx, cvv in enumerate(row):
                if idx == 0:
                    continue
                vc_set.discard((row[idx - 1].v, cvv.c))
        vc_log = ", ".join(str(vc) for vc in vc_set) if vc_set else "None"
        return vc_log

    def check_vcv_integrity(self, vcv_set: VcSet) -> str:
        for row in self.reclist:
            for idx, cvv in enumerate(row):
                if idx == 0:
                    continue
                vcv_set.discard((row[idx - 1].v, cvv.get_cv()))
        vcv_log = ", ".join(str(vcv) for vcv in vcv_set) if vcv_set else "None"
        return vcv_log

    def check_vr_integrity(self, vr_set: set[str]) -> str:
        for row in self.reclist:
            vr_set.discard(row[-1].v)
        vr_log = ", ".join(vr_set) if vr_set else "None"
        return vr_log
