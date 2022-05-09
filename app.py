from cvvc_reclist_generator.cvvc_reclist_generator import CvvcReclistGenerator
from cvvc_reclist_generator.errors import (
    AliasConfigNotFindError,
    ConfigError,
    ConfigNotFindError,
    RedirectConfigNotFindError,
    UnknownError,
)


def print_continue():
    print("press ctrl-C to exit or fix the error manually")
    input("press any key to continue if you've fixed: ")


def main():
    generator = CvvcReclistGenerator()

    try:
        generator.generate()
    except ConfigNotFindError:
        print("Can not find parameter config in default path:")
        print_continue()
        main()
    except (AliasConfigNotFindError, RedirectConfigNotFindError) as e:
        print(f"{e} in your config setting.")
        print_continue()
        main()
    except ValueError as e:
        print(f"{e}")
        print_continue()
        main()
    except ConfigError as e:
        print(f"e")
        print_continue()
        main()


if __name__ == "__main__":
    try:
        main()
        input("output success! press any key to finish.")
    except UnknownError as e:
        print(f"{e} error happened, please contact the author")
