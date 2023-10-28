from .cvvc_reclist_generator_model import Parameters
from .main_window import MainWindow


class CvvcReclistGeneratorGui:
    def __init__(self):
        self.parameters = Parameters()
        self.main_window = MainWindow(self.parameters)

        self.main_window.show()
