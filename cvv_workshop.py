import configparser
from random import choice
from typing import Optional
from alias import AliasType
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
    redirect_consonant_dict: dict[str, list[str]] = field(default_factory=dict)
    redirect_vowel_dict: dict[str, list[str]] = field(default_factory=dict)
    
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

    def find_next(self, vc: tuple[str, str], vc_max_v: str) -> Cvv:
        try:
            next_cv = self.find_cvv(c=vc[1], v=vc_max_v)
        except ValueError:
            next_cv = self.find_cvv(c=vc[1])
        return next_cv

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
        
    def get_redirect_phoneme(self, phoneme: str | tuple[str, str], alias_type: AliasType) -> list[str]:
        redirect_phoneme: list[str] = []
        if alias_type == AliasType.C:
            return redirect_phoneme
                    
        elif alias_type == AliasType.CV:
            
            if phoneme in self.cv_dict:
                for cvv in self.cv_dict.get(str(phoneme), []):
                    _, c, v = cvv.get_lsd_cvv()
                    redirect_phoneme.append(f'{c} {v}')
                    
        elif alias_type == AliasType.VC:
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
                        
        elif alias_type == AliasType.VR:
            for redirect_vowel in self.redirect_vowel_dict.get(str(phoneme), []):
                redirect_phoneme.append(f'{redirect_vowel} ')
                
        else:
            raise TypeError('Given wrong alias type!')
        
        return redirect_phoneme

    def save_presamp(self, presamp_dir: str) -> None:
        presamp_ini: list[str] = ['[VERSION]\n'
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

    def save_lsd(self, lsd_dir: str) -> None:
        with open(lsd_dir, mode='w', encoding='utf-8') as f:
            lsd_str = []
            for cvv in sorted(self.cvv_set, key=Cvv.get_lsd_c):
                cv, c, v = cvv.get_lsd_cvv()
                if c == v:
                    lsd_str.append(f'{cv}\n#{v}')
                else:
                    lsd_str.append(f'{cv}\n{c}#{v}')
            f.write('\n'.join(lsd_str))
            