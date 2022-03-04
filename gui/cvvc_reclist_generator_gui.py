from .main_window import Ui_MainWindow
from PySide6.QtWidgets import QMainWindow

class CvvcReclistGeneratorGui(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()
