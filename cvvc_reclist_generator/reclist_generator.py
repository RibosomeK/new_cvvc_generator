from operator import attrgetter
from typing import Optional
from .data_struct import (
    Cvv,
    AliasType,
    Alias,
    Recline,
    Reclist,
    AliasUnion,
    CvvWorkshop,
)

from .errors import CantFindNextCvvError, CantFindCvvError, PopError


ORDER = {0: "cvv", 1: "v"}


class ReclistGenerator:
    """a reclist generator"""

    def __init__(self, cvv_workshop: CvvWorkshop, order_by: int = 0) -> None:
        self.cvv_workshop = cvv_workshop
        if order_by not in ORDER:
            order_by = 0
        self.order_by: int = order_by
        self.reclist = Reclist()
        self.EMPTY_CVV = Cvv.new()

    def gen_2mora(self, alias_union: AliasUnion) -> None:
        all_cv = alias_union.cv
        for cv_head in alias_union.cv_head.copy():
            cv = Alias(cv_head.alias, AliasType.CV)
            all_cv.add(cv)
        all_cvv = sorted(
            [self.cvv_workshop.find_cvv(cv.alias[0]) for cv in all_cv],
            key=attrgetter(ORDER[self.order_by], ORDER[0]),
        )
        for cvv in all_cvv:
            if cvv:
                line = Recline((cvv, cvv))
                self.reclist.append(line)
                alias_union.c_head.discard(Alias(cvv.get_lsd_c(), AliasType.C_HEAD))
                alias_union.vc.discard(Alias((cvv.v, cvv.c), AliasType.VC))
                alias_union.vcv.discard(Alias((cvv.v, cvv.get_cv()), AliasType.VCV))
                alias_union.v.discard(Alias(cvv.v, AliasType.V))

        if alias_union.vcv:
            vcv_list = list(alias_union.vcv)
            vcv_list.sort(
                key=lambda alias: alias[int(not bool(self.order_by))] + alias[0]
            )
            for vcv in vcv_list:
                v = Cvv.new_with((AliasType.V, vcv[0]))
                cvv = self.cvv_workshop.find_cvv(cvv=vcv[1])
                line = Recline((v, cvv))
                self.reclist.append(line)
                alias_union.vc.discard(Alias((v.v, cvv.c), AliasType.VC))
                alias_union.v.discard(Alias(cvv.v, AliasType.V))
        vc_list = list(alias_union.vc)
        vc_list.sort(key=lambda alias: alias[int(not bool(self.order_by))] + alias[0])
        for vc in vc_list:
            v = Cvv.new_with((AliasType.V, vc[0]))
            c = Cvv.new_with((AliasType.C, vc[1]))
            line = Recline((v, c))
            self.reclist.append(line)

        if c_head_list := sorted(
            alias_union.c_head, key=lambda alias: alias[0], reverse=True
        ):
            row: list[Cvv] = []
            while c_head_list:
                c_head = c_head_list.pop()
                c_head = Cvv.new(("", "", "", str(c_head)))
                if len(row) < 3:
                    row.extend([c_head, self.EMPTY_CVV])
                else:
                    self.reclist.append(Recline(row))
                    row.clear()
            if row:
                self.reclist.append(Recline(row))

        if vr_list := sorted(alias_union.v, key=lambda alias: alias[0], reverse=True):
            row: list[Cvv] = []
            while vr_list:
                vr = vr_list.pop()
                vr = Cvv.new(("", "", str(vr)))
                if len(row) < 3:
                    row.extend([vr, self.EMPTY_CVV])
                else:
                    self.reclist.append(Recline(row))
                    row.clear()
            if row:
                self.reclist.append(Recline(row))

    def gen_plan_b(self, alias_union: AliasUnion) -> AliasUnion:
        all_cv = alias_union.cv.copy()
        for cv_head in alias_union.cv_head.copy():
            cv = Alias(cv_head.alias, AliasType.CV)
            all_cv.add(cv)
        all_cv = sorted(
            [self.cvv_workshop.find_cvv(cv.alias[0]) for cv in all_cv],
            key=attrgetter(ORDER[self.order_by], ORDER[0]),
        )
        for cv in all_cv:
            line = Recline((cv, cv, cv))
            self.reclist.append(line)
            alias_union.c_head.discard(Alias(cv.get_lsd_c(), AliasType.C_HEAD))
            alias_union.vc.discard(Alias((cv.v, cv.c), AliasType.VC))
            alias_union.v.discard(Alias(cv.v, AliasType.V))
            alias_union.vcv.discard(Alias((cv.v, cv.get_cv()), AliasType.VCV))

        alias_union.cv.clear()
        alias_union.cv_head.clear()
        return alias_union

    def gen_mora_x(
        self, alias_union: AliasUnion, length: int, order_length: Optional[int] = None
    ) -> None:
        """Generate given x length long pre row of reclist.

        Args:
            alias_union (AliasUnion): Needed alias
            length (int): length pre row
        Returns: None
        """
        if order_length is None:
            order_length = length

        cvv_list = sorted(
            [self.cvv_workshop.find_cvv(cv.alias[0]) for cv in alias_union.cv],
            key=attrgetter(ORDER[self.order_by], ORDER[0]),
            reverse=True,
        )
        row: list[Cvv] = []
        while cvv_list:
            cvv = cvv_list.pop()
            if len(row) == 0:
                row.append(cvv)
                alias_union.cv_head.discard(
                    Alias(cvv.get_cv(alias_union.is_full_cv), AliasType.CV_HEAD)
                )
                alias_union.c_head.discard(Alias(cvv.get_lsd_c(), AliasType.C_HEAD))
            elif len(row) < order_length:
                pre_cvv = row[-1]
                row.append(cvv)
                alias_union.cv.discard(
                    Alias(cvv.get_cv(alias_union.is_full_cv), AliasType.CV)
                )
                alias_union.vc.discard(Alias((pre_cvv.v, cvv.c), AliasType.VC))
                alias_union.vcv.discard(
                    Alias(
                        (pre_cvv.v, cvv.get_cv(alias_union.is_full_cv)), AliasType.VCV
                    )
                )

            if len(row) == order_length:
                self.reclist.append(Recline(row))
                alias_union.v.discard(Alias(cvv.v, AliasType.V))
                row.clear()

        if row:
            self.reclist.append(Recline(row))
            alias_union.v.discard(Alias(row[-1].v, AliasType.V))
            row.clear()

        def discard_cv(row: list[Cvv], alias_union: AliasUnion) -> None:
            """iter roll to discard cv"""
            for cvv in row[1:]:
                cv = Alias(cvv.get_cv(alias_union.is_full_cv), AliasType.CV)
                alias_union.cv.discard(cv)

        # complete vcv part
        i = 0
        while alias_union.vcv:
            if i == 0:
                vcv = alias_union.vcv.pop_by(v=alias_union.vcv.max_v[0])
                v_cvv = self.cvv_workshop.find_cvv(v=vcv[0])
                cv_cvv = self.cvv_workshop.find_cvv(cvv=vcv[1])
                alias_union.vc.discard(Alias((v_cvv.v, cv_cvv.c), AliasType.VC))
                row = [v_cvv, cv_cvv]
                i += 2
            elif i <= length - 1:
                try:
                    vcv = alias_union.vcv.pop_by(v=row[-1].v)
                    try:
                        next_cv = self.cvv_workshop.find_cvv(cvv=vcv[1])
                    except CantFindNextCvvError:
                        next_cv = self.cvv_workshop.find_cvv(c=vcv[1])
                    alias_union.vc.discard(Alias((vcv[0], next_cv.c), AliasType.VC))
                    row.append(next_cv)
                    i += 1
                except PopError:
                    if i <= length - 2:
                        vcv = alias_union.vcv.pop()
                        cv1 = self.cvv_workshop.find_cvv(v=vcv[0])
                        cv2 = self.cvv_workshop.find_cvv(cvv=vcv[1])
                        alias_union.vc.discard(Alias((row[-1].v, cv1.c), AliasType.VC))
                        alias_union.vc.discard(Alias((cv1.v, cv2.c), AliasType.VC))
                        row.extend([cv1, cv2])
                        i += 2
                    else:
                        i = length
                        continue
            elif i == length:
                self.reclist.append(Recline(row))
                discard_cv(row, alias_union)
                alias_union.v.discard(Alias(row[-1].v, AliasType.V))
                alias_union.c_head.discard(Alias(row[0].get_lsd_c(), AliasType.C_HEAD))
                alias_union.cv_head.discard(
                    Alias(row[0].get_cv(alias_union.is_full_cv), AliasType.CV_HEAD)
                )
                row: list[Cvv] = []
                i = 0
        if row:
            self.reclist.append(Recline(row))
            discard_cv(row, alias_union)
            alias_union.v.discard(Alias(row[-1].v, AliasType.V))
            alias_union.c_head.discard(Alias(row[0].get_lsd_c(), AliasType.C_HEAD))
            alias_union.cv_head.discard(
                Alias(row[0].get_cv(alias_union.is_full_cv), AliasType.CV_HEAD)
            )

        # complete the vc part
        row: list[Cvv] = []
        i = 0
        while alias_union.vc:
            if i == 0:
                current_v = alias_union.vc.max_v[0]
                current_cv = self.cvv_workshop.find_cvv(v=current_v)
                current_vc = alias_union.vc.pop_by(v=current_v)
                row.append(current_cv)
                try:
                    next_cv = self.cvv_workshop.find_next(
                        current_vc.alias, alias_union.vc.max_v[0]
                    )
                except CantFindNextCvvError:
                    next_cv = self.cvv_workshop.find_cvv(c=current_vc[1])
                row.append(next_cv)
                i += 2
            elif i <= length - 1:
                try:
                    vc = alias_union.vc.pop_by(v=row[-1].v)
                    try:
                        row.append(
                            self.cvv_workshop.find_next(
                                vc.alias, alias_union.vc.max_v[0]
                            )
                        )
                    except CantFindNextCvvError:
                        row.append(self.cvv_workshop.find_cvv(c=vc[1]))
                    i += 1
                except PopError:
                    if i <= length - 2:
                        vc = alias_union.vc.pop()
                        cv1 = self.cvv_workshop.find_cvv(v=vc[0])
                        try:
                            cv2 = self.cvv_workshop.find_cvv(
                                c=vc[1], v=alias_union.vc.max_v[0]
                            )
                        except CantFindCvvError:
                            cv2 = self.cvv_workshop.find_cvv(c=vc[1])
                        row.extend([cv1, cv2])
                        i += 2
                    else:
                        i = length
                        continue
            elif i == length:
                self.reclist.append(Recline(row))
                alias_union.v.discard(Alias(row[-1].v, AliasType.V))
                alias_union.c_head.discard(Alias(row[0].get_lsd_c(), AliasType.C_HEAD))
                alias_union.cv_head.discard(
                    Alias(row[0].get_cv(alias_union.is_full_cv), AliasType.CV_HEAD)
                )
                row: list[Cvv] = []
                i = 0
        if row:
            self.reclist.append(Recline(row))
            discard_cv(row, alias_union)
            alias_union.v.discard(Alias(row[-1].v, AliasType.V))
            alias_union.c_head.discard(Alias(row[0].get_lsd_c(), AliasType.C_HEAD))
            alias_union.cv_head.discard(
                Alias(row[0].get_cv(alias_union.is_full_cv), AliasType.CV_HEAD)
            )

        # complete cv part
        cvv_list = sorted(
            [self.cvv_workshop.find_cvv(cv.alias[0]) for cv in alias_union.cv],
            key=attrgetter(ORDER[self.order_by], ORDER[0]),
            reverse=True,
        )
        ALPHA = sorted(self.cvv_workshop.cvv_set, key=lambda cvv: cvv.get_cv())[0]
        row: list[Cvv] = []
        while cvv_list:
            if len(row) == 0:
                if alias_union.cv_head:
                    row.append(
                        self.cvv_workshop.find_cvv(cvv=str(alias_union.cv_head.pop()))
                    )
                    alias_union.c_head.discard(
                        Alias(row[0].get_lsd_c(), AliasType.C_HEAD)
                    )
                else:
                    row.append(ALPHA)
            elif len(row) < order_length:
                cvv = cvv_list.pop()
                row.append(cvv)
            else:
                self.reclist.append(Recline(row))
                vr = Alias(row[-1].v, AliasType.V)
                alias_union.v.discard(vr)
                row.clear()
        if row:
            self.reclist.append(Recline(row))
            vr = Alias(row[-1].v, AliasType.V)
            alias_union.v.discard(vr)

        # complete cv head part
        cvv_head_list = sorted(
            [self.cvv_workshop.find_cvv(cv.alias[0]) for cv in alias_union.cv_head],
            key=attrgetter(ORDER[self.order_by], ORDER[0]),
            reverse=True,
        )
        row: list[Cvv] = []
        while cvv_head_list:
            for i in range(order_length // 2 + order_length % 2):
                if not cvv_head_list:
                    break
                row.append(cvv_head_list.pop())
                alias_union.v.discard(Alias(row[-1].v, AliasType.V))
                alias_union.c_head.discard(Alias(row[-1].get_lsd_c(), AliasType.C_HEAD))
                row.append(self.EMPTY_CVV)
            if row[-1] == self.EMPTY_CVV:
                row.pop()
            self.reclist.append(Recline(row))
            row: list[Cvv] = []
        alias_union.cv_head.clear()

        # complete c head part
        c_head_list = list(
            sorted(alias_union.c_head, key=lambda alias: alias[0], reverse=True)
        )
        row: list[Cvv] = []
        while c_head_list:
            for i in range(order_length // 2 + order_length % 2):
                if not c_head_list:
                    break
                c_head = c_head_list.pop()
                for cvv in self.cvv_workshop.cvv_set:
                    if cvv.get_lsd_c() == c_head.alias[0]:
                        c_head = cvv
                        break
                else:
                    raise CantFindCvvError(f"no cvv has consonant {c_head}")
                row.extend((c_head, self.EMPTY_CVV))
                alias_union.v.discard(Alias(c_head.v, AliasType.V))
            if row[-1] == self.EMPTY_CVV:
                row.pop()
            self.reclist.append(Recline(row))
            row.clear()
        alias_union.c_head.clear()

        # complete ending v part
        vr_list = sorted(alias_union.v, key=lambda alias: alias[0], reverse=True)
        row: list[Cvv] = []
        while vr_list:
            for i in range(order_length // 2 + order_length % 2):
                if not vr_list:
                    break
                row.append(self.cvv_workshop.find_cvv(v=str(vr_list.pop())))
                row.append(self.EMPTY_CVV)
            if row[-1] == self.EMPTY_CVV:
                row.pop()
            self.reclist.append(Recline(row))
            row: list[Cvv] = []
        alias_union.v.clear()

    def save_reclist(self, reclist_dir: str) -> None:
        with open(reclist_dir, mode="w", encoding="utf-8") as fp:
            fp.write(str(self.reclist))

    @staticmethod
    def export_reclist(
        reclist: Reclist, reclist_path: str = "./result/reclist.txt"
    ) -> None:
        with open(reclist_path, mode="w", encoding="utf-8") as fp:
            fp.write(str(reclist))
