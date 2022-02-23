from layout_classes import (SelectDictFileLayout, SelectRedirectFileLayout, 
    SelectAliasConfigFileLayout, ReclistDetailLayout, ReclistStyleLayout, 
    LabelStyleLayout, SaveFileSpeciesLayout, SelectSaveDirPath, BottomButtonLayout)
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    
    overall_layout: QVBoxLayout

    select_dict_file_layout: SelectDictFileLayout
    select_redirect_dir_layout: SelectRedirectFileLayout
    select_alias_config_file_layout: SelectAliasConfigFileLayout
    reclist_style_layout: ReclistStyleLayout
    reclist_detail_layout: ReclistDetailLayout
    label_style_layout:  LabelStyleLayout
    select_save_dir_layout: SelectSaveDirPath
    save_file_species: SaveFileSpeciesLayout
    bottom_button_layout: BottomButtonLayout
    
    widget: QWidget
    
    def __init__(self) -> None:
        super().__init__()
        self.__init_layout()
        self.setWindowTitle('cvvc reclist generator')
        self.click_check_param()
    
    def __init_layout(self) -> None:
        self.select_dict_file_layout = SelectDictFileLayout()
        self.select_redirect_dir_layout = SelectRedirectFileLayout()
        self.select_alias_config_file_layout = SelectAliasConfigFileLayout()
        self.reclist_style_layout = ReclistStyleLayout()
        self.reclist_detail_layout = ReclistDetailLayout()
        self.label_style_layout =  LabelStyleLayout()
        self.select_save_dir_layout = SelectSaveDirPath()
        self.save_file_species = SaveFileSpeciesLayout()
        self.bottom_button_layout = BottomButtonLayout()
        
        self.overall_layout = QVBoxLayout()
        self.overall_layout.addLayout(self.select_dict_file_layout)
        self.overall_layout.addLayout(self.select_redirect_dir_layout)
        self.overall_layout.addLayout(self.select_alias_config_file_layout)
        self.overall_layout.addLayout(self.reclist_style_layout)
        self.overall_layout.addLayout(self.reclist_detail_layout)
        self.overall_layout.addLayout(self.label_style_layout)
        self.overall_layout.addLayout(self.select_save_dir_layout)
        self.overall_layout.addLayout(self.save_file_species)
        self.overall_layout.addLayout(self.bottom_button_layout)
        
        self.widget = QWidget()
        self.widget.setLayout(self.overall_layout)
        self.setCentralWidget(self.widget)
        
    def click_check_param(self) -> None:
        self.bottom_button_layout.preview_button.clicked.connect(self.check_param)
        self.bottom_button_layout.save_button.clicked.connect(self.check_param)
        
    def check_param(self):
        if self.select_dict_file_layout.line_view.text() == '':
            raise SyntaxError
        if (not self.reclist_style_layout.two_mora_check_box.isChecked() 
            and not self.reclist_style_layout.haru_style_check_box.isChecked()
            and not self.reclist_style_layout.mora_x_check_box.isChecked()
            ):
            raise SyntaxError
        
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec()