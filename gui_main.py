from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator
from py_gui.cvvc_reclist_generator_gui import CvvcReclistGeneratorGui


if __name__ == "__main__":
    app = QApplication([])
    win = CvvcReclistGeneratorGui()

    app.exec()
