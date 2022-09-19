from .cvvc_reclist_generator import CvvcReclistGenerator
from .errors import (
    ConfigNotFoundError,
    AliasConfigNotFoundError,
    RedirectConfigNotFoundError,
    DictFileNotFoundError,
)


class GeneratorErrorManager:
    """this class is to handle raise error happen while generate reclist"""

    def __init__(self, generator: CvvcReclistGenerator) -> None:
        self.generator = generator

    def __enter__(self):
        return self.generator

    def __exit__(self, exc_type, exc_val, exc_tb):
        """handle raise errors"""

        if exc_type == ConfigNotFoundError:
            print("Can not find parameter config in default path: ./")
            print_solution()
            return True

        if exc_type == DictFileNotFoundError:
            print(
                f"Can not find dict file in given directory: \n{self.generator.parameters.dict_file}"
            )
            print_solution()
            return True

        if exc_type == AliasConfigNotFoundError:
            print(
                f"Can not find alias config in given directory: \n{self.generator.parameters.alias_config}"
            )
            print_solution()
            return True

        if exc_type == RedirectConfigNotFoundError:
            print(
                f"Can not find redirect config in given directory: \n{self.generator.parameters.redirect_config}"
            )
            print_solution()
            return True

        return False


def print_solution():
    print("press ctrl-C to exit or fix the error manually")
    input("press any key to continue if you've fixed: ")
