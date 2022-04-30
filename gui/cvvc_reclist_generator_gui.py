from PySide6.QtCore import QTranslator
from .cvvc_reclist_generator_model import Parameters
from .main_window import MainWindow
from .preview_dialog import PreviewDialog


class CvvcReclistGeneratorGui:
    def __init__(self):
        self.translator = QTranslator()

        self.parameters = Parameters()
        self.main_window = MainWindow(self.parameters)
        self.preview_dialog = PreviewDialog()

        self.main_window.show()
