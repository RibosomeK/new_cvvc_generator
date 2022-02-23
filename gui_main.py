from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from cvv_dataclasses import *
from alias_union_generator import AliasUnionGenerator
from reclist_generator import ReclistGenerator
from reclist_checker import ReclistChecker
from oto_generator import OtoGenerator
from vsdxmf_generator import VsdxmfGenerator


class CVVCReclistGenerator:
    
    app: QApplication
    main_window: MainWindow
    
    def __init__(self) -> None:
        self.__init_gui()
        
    
    def __init_gui(self) -> None:
        self.app = QApplication([])
        self.main_window = MainWindow()
        self.main_window.show()
        self.app.exec()
        
    


def main():
    generator = CVVCReclistGenerator()
    
    
if __name__ == '__main__':
    main()
    