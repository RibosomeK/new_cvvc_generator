from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, 
                               QSpinBox, QWidget, QMainWindow, QLabel, 
                               QLineEdit, QCheckBox, QApplication)


class MainWindow(QMainWindow):
    overall_layout = QVBoxLayout()
        
    select_dict_file_layout = QHBoxLayout()
    select_redirect_dir_layout = QHBoxLayout()
    select_alias_config_file_layout = QHBoxLayout()
    select_reclist_style_layout = QHBoxLayout()
    select_reclist_detail_layout = QHBoxLayout()
    select_label_style_layout =  QHBoxLayout()
    select_save_dir_layout = QHBoxLayout()
    select_save_file_species = QHBoxLayout()
    bottom_button_layout = QHBoxLayout()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('cvvc reclist generator')
        self.overall_layout_adding()
        widget = QWidget()
        widget.setLayout(self.overall_layout)
        self.setCentralWidget(widget)
        
    def overall_layout_adding(self) -> None:
        self.overall_layout.addLayout(self.get_select_dict_file_layout())
        self.overall_layout.addLayout(self.get_select_redirect_config_layout())
        self.overall_layout.addLayout(self.get_select_alias_config_file_layout())
        self.overall_layout.addLayout(self.get_reclist_style_layout())
        self.overall_layout.addLayout(self.get_reclist_detail_layout())
        self.overall_layout.addLayout(self.get_label_style_layout())
        self.overall_layout.addLayout(self.get_select_save_dir_layout())
        self.overall_layout.addLayout(self.get_select_save_file_species_layout())
        self.overall_layout.addLayout(self.get_bottom_button_layout())
        
    def get_select_dict_file_layout(self) -> QHBoxLayout:
        line_view = QLineEdit()
        line_view.setReadOnly(True)
        button = QPushButton('Select')
        self.select_dict_file_layout.addWidget(QLabel('Dict file: '))
        self.select_dict_file_layout.addWidget(line_view)
        self.select_dict_file_layout.addWidget(button)
        return self.select_dict_file_layout
    
    def get_select_redirect_config_layout(self) -> QHBoxLayout:
        line_view = QLineEdit()
        line_view.setReadOnly(True)
        button = QPushButton('Select')
        self.select_redirect_dir_layout.addWidget(QLabel('Redirect file: '))
        self.select_redirect_dir_layout.addWidget(line_view)
        self.select_redirect_dir_layout.addWidget(button)
        return self.select_redirect_dir_layout
        
    def get_select_alias_config_file_layout(self) -> QHBoxLayout:
        line_view = QLineEdit()
        line_view.setReadOnly(True)
        button = QPushButton('Select')
        self.select_alias_config_file_layout.addWidget(QLabel('Alias config file: '))
        self.select_alias_config_file_layout.addWidget(line_view)
        self.select_alias_config_file_layout.addWidget(button)
        return self.select_alias_config_file_layout
    
    def get_reclist_style_layout(self) -> QHBoxLayout:
        two_mora_check_box = QCheckBox('2 mora')
        haru_style_check_box = QCheckBox('Haru style')
        x_mora_check_box = QCheckBox('X mora')
        self.select_reclist_style_layout.addWidget(QLabel('Reclist style: '))
        self.select_reclist_style_layout.addWidget(two_mora_check_box)
        self.select_reclist_style_layout.addWidget(haru_style_check_box)
        self.select_reclist_style_layout.addWidget(x_mora_check_box)
        return self.select_reclist_style_layout
    
    def get_reclist_detail_layout(self) -> QHBoxLayout:
        length_spin_box = QSpinBox()
        length_spin_box.setMinimum(3)
        is_cv_head_check_box = QCheckBox('CV head')
        is_c_head_check_box = QCheckBox('C head')
        is_cv_mid_check_box = QCheckBox('CV mid')
        is_full_cv_check_box = QCheckBox('Full CV')
        self.select_reclist_detail_layout.addWidget(QLabel('Reclist detail: '))
        self.select_reclist_detail_layout.addWidget(length_spin_box)
        self.select_reclist_detail_layout.addWidget(QLabel('Length'))
        self.select_reclist_detail_layout.addWidget(is_cv_head_check_box)
        self.select_reclist_detail_layout.addWidget(is_c_head_check_box)
        self.select_reclist_detail_layout.addWidget(is_cv_mid_check_box)
        self.select_reclist_detail_layout.addWidget(is_full_cv_check_box)
        return self.select_reclist_detail_layout
    
    def get_label_style_layout(self) -> QHBoxLayout:
        bpm_spin_box = QSpinBox()
        bpm_spin_box.setRange(100, 200)
        bpm_spin_box.setSingleStep(10)
        blank_beat = QSpinBox()
        blank_beat.setRange(0, 10)
        self.select_label_style_layout.addWidget(QLabel('Label style: '))
        self.select_label_style_layout.addWidget(bpm_spin_box)
        self.select_label_style_layout.addWidget(QLabel('bpm'))
        self.select_label_style_layout.addWidget(blank_beat)
        self.select_label_style_layout.addWidget(QLabel('blank beat'))
        return self.select_label_style_layout
    
    def get_select_save_dir_layout(self) -> QHBoxLayout:
        line_view = QLineEdit()
        line_view.setReadOnly(True)
        button = QPushButton('Select')
        self.select_save_dir_layout.addWidget(QLabel('Save dir path: '))
        self.select_save_dir_layout.addWidget(line_view)
        self.select_save_dir_layout.addWidget(button)
        return self.select_save_dir_layout
    
    def get_select_save_file_species_layout(self) -> QHBoxLayout:
        self.select_save_file_species.addWidget(QCheckBox('oto'))
        self.select_save_file_species.addWidget(QCheckBox('presamp'))
        self.select_save_file_species.addWidget(QCheckBox('vsdxmf'))
        self.select_save_file_species.addWidget(QCheckBox('lsd'))
        return self.select_save_file_species
    
    def get_bottom_button_layout(self) -> QHBoxLayout:
        self.bottom_button_layout.addWidget(QPushButton('Preview'))
        self.bottom_button_layout.addWidget(QPushButton('Save'))
        return self.bottom_button_layout
    
    
def main():
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec()
    
    
if __name__ == '__main__':
    main()