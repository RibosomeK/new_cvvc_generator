

class WrongArgumentsNumberError(Exception):
    """ginven the wrong number of arguments"""
    
    
class MissingCvInPresampError(Exception):
    """existed cv must be included in [CONSONANT] section"""
    

class MultiCvInPresampError(Exception):
    """existed cv appeared multiple"""
    
    
class CantFindCvvError(Exception):
    """cannot find a cvv type[Cvv] with given arguments"""
    

class CantFindNextCvvError(Exception):
    """cannot find a cvv under given condition"""
    
    
class ArgumentTypeError(Exception):
    """the type of given argument is invalid"""
    

class AliasConfigTypeError(Exception):
    """type in alias config is invalid"""
    
    
class AliasTypeError(Exception):
    """given type of alias is invalid"""
    
    
class AliasNotExistError(Exception):
    """alias does not exist in given dict config"""
    
    
class PopError(Exception):
    """no qualified vc in set"""