from PySide6.QtWidgets import QApplication
from py_gui.cvvc_reclist_generator_gui import CvvcReclistGeneratorGui


if __name__ == "__main__":
    app = QApplication([])
    win = CvvcReclistGeneratorGui()

    app.exec()
