import json
from typing import Iterable, Optional
from .data_struct import Alias, AliasType, AliasUnion, CvvWorkshop
from .errors import AliasTypeError, AliasError


class AliasUnionGenerator:
    """get needed alias."""

    def __init__(self, cvv_workshop: CvvWorkshop) -> None:
        self.cvv_workshop = cvv_workshop

    def get_needed_alias(
        self,
        is_c_head: bool = False,
        is_cv_head: bool = True,
        is_full_cv: bool = True,
        alias_config: Optional[str] = None,
    ) -> AliasUnion:
        """Get needed alias.

        Args:
            c_head (bool, optional): Beginning consonant for vocalsharp. Defaults to False.
            cv_head (bool, optional): Beginning cv head. Defaults to True.
            is_full_cv (bool, optional): For cv and cv head.
                If your dict included extra cv part and you WANT TO use them in non vcv part,
                you must set to False. Defaults to True.
            alias_config (Optional[str], optional): exceptional alias config. Defaults to None.

        Returns:
            AliasUnion
        """
        alias_union = AliasUnion()
        self.is_full_cv = is_full_cv

        if is_c_head:
            alias_union.c_head = {
                Alias(x.get_lsd_c(), AliasType.C_HEAD)
                for x in self.cvv_workshop.cvv_set
                if x.v != x.get_lsd_c()
            }
        alias_union.cv = {
            Alias(cv.get_cv(is_full_cv), AliasType.CV)
            for cv in self.cvv_workshop.cvv_set
        }
        if is_cv_head:
            for alias in alias_union.cv:
                head_alias = Alias(alias.alias, AliasType.CV_HEAD)
                alias_union.cv_head.add(head_alias)
        alias_union.vc.update(
            Alias((v, c), AliasType.VC)
            for v in self.cvv_workshop.v_dict
            for c in self.cvv_workshop.c_dict
        )
        alias_union.v = {Alias(v, AliasType.V) for v in self.cvv_workshop.v_dict}
        if alias_config:
            unneeded, needed = self.read_alias_config(alias_config, is_full_cv)
            alias_union.update(needed)
            alias_union.difference_update(unneeded)
        if alias_union.vcv:
            alias_union.vcv.difference_update(alias_union.vc)
        return alias_union

    def read_alias_config(
        self, alias_config_path: str, is_full_cv: bool = True
    ) -> tuple[AliasUnion, AliasUnion]:
        """read an alias json file and return two alias union"""

        unneeded_dict, needed_dict = self._open_and_check(alias_config_path)
        unneeded = self._read_alias_dict(unneeded_dict, is_full_cv)
        needed = self._read_alias_dict(needed_dict, is_full_cv)
        return unneeded, needed

    def _read_alias_dict(self, alias_dict: dict, is_full_cv: bool = True) -> AliasUnion:
        alias_union = AliasUnion()

        if isinstance(alias_dict["C_HEAD"], str):
            alias_union.c_head.update(
                [
                    Alias(c_head, AliasType.C_HEAD)
                    for c_head in self.cvv_workshop.c_dict.keys()
                ]
            )
        else:
            alias_union.c_head.update(alias_dict["C_HEAD"])

        if isinstance(alias_dict["C"], str):
            alias_union.c.update(
                [Alias(c, AliasType.C) for c in self.cvv_workshop.c_dict.keys()]
            )
        else:
            alias_union.c.update([Alias(c, AliasType.C) for c in alias_dict["C"]])

        alias_union.v.update(Alias(v, AliasType.V) for v in alias_dict["VR"])

        # cv part func
        def update_cv(
            cv_type: str,
            cv_alias_dict: dict[str, list[str]],
            update_alias_union: AliasUnion,
        ):
            for alias_type, alias in loop_in_dict(cv_alias_dict):
                if alias_type == "c":
                    for consonant in alias:
                        if cv_type == "cv":
                            update_alias_union.cv.update(
                                (
                                    Alias(
                                        cvv.get_cv(is_full_cv=is_full_cv), AliasType.CV
                                    )
                                    for cvv in self.cvv_workshop.c_dict[consonant]
                                )
                            )
                        else:
                            update_alias_union.cv_head.update(
                                (
                                    Alias(
                                        cvv.get_cv(is_full_cv=is_full_cv),
                                        AliasType.CV_HEAD,
                                    )
                                    for cvv in self.cvv_workshop.c_dict[consonant]
                                )
                            )
                elif alias_type == "v":
                    for vowel in alias:
                        if cv_type == "cv":
                            update_alias_union.cv.update(
                                (
                                    Alias(
                                        cvv.get_cv(is_full_cv=is_full_cv), AliasType.CV
                                    )
                                    for cvv in self.cvv_workshop.v_dict[vowel]
                                )
                            )
                        else:
                            update_alias_union.cv_head.update(
                                (
                                    Alias(
                                        cvv.get_cv(is_full_cv=is_full_cv),
                                        AliasType.CV_HEAD,
                                    )
                                    for cvv in self.cvv_workshop.v_dict[vowel]
                                )
                            )

                elif alias_type == "cv":
                    if cv_type == "cv":
                        update_alias_union.cv.update(
                            Alias(cv, AliasType.CV) for cv in alias
                        )
                    else:
                        update_alias_union.cv_head.update(
                            Alias(cv, AliasType.CV_HEAD) for cv in alias
                        )

        update_cv("cv", alias_dict["CV"], alias_union)
        update_cv("cv_head", alias_dict["CV_HEAD"], alias_union)

        # vc part
        for alias_type, alias in loop_in_dict(alias_dict["VC"]):
            if alias_type == "c":
                for consonant in alias:
                    alias_union.vc.update(
                        (
                            Alias((v, consonant), AliasType.VC)
                            for v in self.cvv_workshop.v_dict
                        )
                    )
            elif alias_type == "v":
                for vowel in alias:
                    alias_union.vc.update(
                        (
                            Alias((vowel, c), AliasType.VC)
                            for c in self.cvv_workshop.c_dict
                        )
                    )
            elif alias_type == "vc":
                for vc in alias:
                    v, c = vc.split(" ")
                    alias_union.vc.add(Alias((v, c), AliasType.VC))

        # vcv part
        for alias_type, alias in loop_in_dict(alias_dict["VCV"]):
            if alias_type == "c":
                for consonant in alias:
                    alias_union.vcv.update(
                        (
                            Alias((v, cvv.get_cv(is_full_cv)), AliasType.VCV)
                            for v in self.cvv_workshop.v_dict
                            for cvv in self.cvv_workshop.c_dict[consonant]
                        )
                    )
            elif alias_type == "v":
                for vowel in alias:
                    alias_union.vcv.update(
                        (
                            Alias((vowel, cvv.get_cv(is_full_cv)), AliasType.VCV)
                            for cvv in self.cvv_workshop.cvv_set
                        )
                    )
            elif alias_type == "cv":
                for cv in alias:
                    alias_union.vcv.update(
                        Alias((v, cv), AliasType.VCV) for v in self.cvv_workshop.v_dict
                    )
            elif alias_type == "vcv":
                if isinstance(alias, str):
                    alias_union.vcv.update(
                        Alias((v, cvv.get_cv(is_full_cv)), AliasType.VCV)
                        for v in self.cvv_workshop.v_dict
                        for cvv in self.cvv_workshop.cvv_set
                    )
                    continue
                for vcv in alias:
                    v, cv = vcv.split(" ")
                    alias_union.vcv.add(Alias((v, cv), AliasType.VCV))

        return alias_union

    def _open_and_check(self, alias_config_path: str) -> tuple[dict, dict]:
        """open an alias json file and check it"""

        with open(alias_config_path, "r") as f:
            d = json.load(f)
            unneeded_dict, needed_dict = d["UNNEEDED"], d["NEEDED"]

        if invalid_alias := self._check_config_section(unneeded_dict):
            print("unneeded alias has following invalid alias:\n", invalid_alias)
            raise AliasError()
        if invalid_alias := self._check_config_section(needed_dict):
            print("needed alias has following invalid alias:\n", invalid_alias)
            raise AliasError()

        return unneeded_dict, needed_dict

    def _check_config_section(self, d_2check: dict) -> dict[str, list[str]]:
        """check whether the alias in one config section are valid or not.

        Args:
            d_2check (dict): loaded dictionary.

        Returns:
            dict[str, list[str]]: return invalid alias.
        """

        invalid_alias: dict = {}

        for name, array in loop_in_dict(d_2check):
            if isinstance(array, str):
                if array.upper() != "ALL":
                    raise SyntaxError(f"{array} is not a valid argument")
                else:
                    continue
            name = name.lower()
            if name in ("c", "c_head"):
                if invalids := self._check_c_validation(array):
                    invalid_alias.setdefault(name, []).extend(invalids)
            elif name in ("vr", "v"):
                if invalids := self._check_v_validation(array):
                    invalid_alias.setdefault(name, []).extend(invalids)
            elif name in ("cv", "cv_head"):
                if invalids := self._check_cv_validation(array):
                    invalid_alias.setdefault(name, []).extend(invalids)
            elif name == "vc":
                for vc in array:
                    v, c = vc.split(" ")
                    if invalids := self._check_v_validation(v):
                        invalid_alias.setdefault(name, []).extend(invalids)
                    if invalids := self._check_c_validation(c):
                        invalid_alias.setdefault(name, []).extend(invalids)
            elif name == "vcv":
                for vcv in array:
                    v, cv = vcv.split(" ")
                    if invalids := self._check_v_validation(v):
                        invalid_alias.setdefault(name, []).extend(invalids)
                    if invalids := self._check_cv_validation(cv):
                        invalid_alias.setdefault(name, []).extend(invalids)
            elif name in ("v", "vr"):
                if invalids := self._check_v_validation(array):
                    invalid_alias.setdefault(name, []).extend(invalids)
            else:
                raise AliasTypeError(f"Alias type: {name} is invalid")

        return invalid_alias

    def _check_c_validation(self, consonants: Iterable) -> tuple[str, ...]:
        """check if the given consonants are valid or not.
        in other words, do they exist in given dictionary.

        Returns:
            tuple[str, ...]: return all invalid consonants.
        """

        return tuple({c for c in consonants if c not in self.cvv_workshop.c_dict})

    def _check_v_validation(self, vowels: Iterable) -> tuple[str, ...]:
        """check if the given vowels are valid or not.
        in other words, do they exist in given dictionary.

        Returns:
            tuple[str, ...]: return all invalid vowels.
        """

        return tuple({v for v in vowels if v not in self.cvv_workshop.v_dict})

    def _check_cv_validation(self, words: Iterable) -> tuple[str, ...]:
        return tuple({cv for cv in words if cv not in self.cvv_workshop.cv_dict})


def loop_in_dict(d: dict):
    """an iterator to loop over all the list(or other) in a dict"""
    for k, v in d.items():
        if isinstance(v, dict):
            loop_in_dict(v)
        else:
            yield k, v
