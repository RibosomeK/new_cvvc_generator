from cvvc_reclist_generator.cvvc_reclist_generator import CvvcReclistGenerator
from cvvc_reclist_generator.error_context_manager import GeneratorErrorManager


def main():

    while True:
        generator = CvvcReclistGenerator()
        with GeneratorErrorManager(generator) as gen:
            gen.generate()
            break
    input("output success! press any key to finish.")


if __name__ == "__main__":
    main()
