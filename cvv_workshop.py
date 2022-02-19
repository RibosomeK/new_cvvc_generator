from random import choice
from typing import Optional
from reclist import Cvv
from dataclasses import dataclass, field


@dataclass
class CvvWorkshop:
    """cvv workshop that store dict information and tool"""
    
    cvv_set: set[Cvv] = field(default_factory=set)
    cvv_dict: dict[str, Cvv] = field(default_factory=dict)
    cv_dict: dict[str, list[Cvv]] = field(default_factory=dict)
    c_dict: dict[str, list[Cvv]] = field(default_factory=dict)
    v_dict: dict[str, list[Cvv]] = field(default_factory=dict)
    
    def read_dict(self, dict_dir: str) -> None:
        """read a cvvc dict in the following format:
            bao,p,ao
            pao,ph,ao
            ...
            guang,k,uang
            kuang,kh,uang
        split symbol \t can also be used
        the format can be also extend for more detail structure of the word,
        more specific can be seen in Oto class

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
                word = Cvv.new(line.split(split_symbol))
                cvv, c, v, *_ = word
                self.cvv_set.add(word)
                self.cvv_dict.setdefault(cvv, word)
                if word.cv:
                    self.cv_dict.setdefault(word.cv, []).append(word)
                self.c_dict.setdefault(c, []).append(word)
                self.v_dict.setdefault(v, []).append(word)

    def find_cvv(self, cvv: str = None, c: str = None, v: str = None, exception: Optional[set[str]] = None) -> Cvv:
        """find a cvv class by a cvv, c, or v

        Args:
            cvv (str, optional): _description_. Defaults to None.
            c (str, optional): _description_. Defaults to None.
            v (str, optional): _description_. Defaults to None.
            exception (Optional[set[str]], optional): _description_. Defaults to None.

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            SyntaxError: _description_

        Returns: Cvv
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
                    new_cvv_list: list[Cvv] = []
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
                    new_cvv_list: list[Cvv] = []
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
