from re import S
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFileDialog, QCheckBox, QSpinBox, QWidget)
from PySide6.QtCore import Qt


class SelectLayout(QHBoxLayout):
    """a select file style layout base class"""
    label: QLabel
    line_view: QLineEdit
    select_button: QPushButton
    selected_file_name: str = ''
    
    def __init__(self) -> None:
        super().__init__()
        self.__init_layout()
        self.select_button.clicked.connect(self.select_dict_file)
        
    def __init_layout(self):
        self.label = QLabel()
        self.line_view = QLineEdit()
        self.line_view.setReadOnly(True)
        self.select_button = QPushButton('Select')
        self.select_button.setCheckable(True)
        self.addWidget(self.label)
        self.addWidget(self.line_view)
        self.addWidget(self.select_button)
        
    def select_dict_file(self):
        pass


class SelectDictFileLayout(SelectLayout):
        
    def __init__(self) -> None:
        super().__init__()
        self.label.setText('Dict file: ')
        
    def select_dict_file(self):
        """select a dict file, presamp.ini, .lsd is also supported"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_name = file_dialog.getOpenFileName(QWidget(), 
            'Select dict', './', 'Dict File (*.txt);;Presamp File (*.ini);;Lsd File (*.lsd)')[0]
        if file_name != '':
            self.line_view.setText(file_name)
            self.selected_file_name = file_name
        
        
class SelectRedirectFileLayout(SelectLayout):

    def __init__(self) -> None:
        super().__init__()
        self.label.setText('Redirect file: ')
        
    def select_dict_file(self):
        """select a redirect file"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_name = file_dialog.getOpenFileName(QWidget(), 
            'Select redirect config', './', 'Config File (*.ini)')[0]
        if file_name != '':
            self.line_view.setText(file_name)
            self.selected_file_name = file_name
            
            
class SelectAliasConfigFileLayout(SelectLayout):
    
    def __init__(self) -> None:
        super().__init__()
        self.label.setText('Alias file')
        
    def select_dict_file(self):
        """select an alias config file"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_name = file_dialog.getOpenFileName(QWidget(), 
            'Select alias file', './', 'Config File (*.ini)')[0]
        if file_name != '':
            self.line_view.setText(file_name)
            self.selected_file_name = file_name
            
            
class SelectSaveDirPath(SelectLayout):
    
    def __init__(self) -> None:
        super().__init__()
        self.label.setText('Save dir path: ')
        self.line_view.setText('./result')
        
    def select_dict_file(self):
        """select an alias config file"""
        file_dialog = QFileDialog()
        dir_path = file_dialog.getExistingDirectory(QWidget(), 'Select alias file', './',)
        if dir_path != '':
            self.line_view.setText(dir_path)
            self.selected_file_name = dir_path
            

class ReclistStyleLayout(QHBoxLayout):
    
    label: QLabel
    two_mora_check_box: QCheckBox
    haru_style_check_box: QCheckBox
    mora_x_check_box: QCheckBox
    
    def __init__(self) -> None:
        super().__init__()
        self.__init_layout()
        self.two_mora_check_box.stateChanged.connect(self.__uncheck_mora_x)
        self.mora_x_check_box.stateChanged.connect(self.__uncheck_two_mora)
        
    def __init_layout(self) -> None:
        self.label = QLabel('Reclist style: ')
        self.two_mora_check_box = QCheckBox('2 mora')
        self.haru_style_check_box = QCheckBox('Haru.J style')
        self.mora_x_check_box = QCheckBox('x mora')
        self.addWidget(self.label)
        self.addWidget(self.two_mora_check_box)
        self.addWidget(self.haru_style_check_box)
        self.addWidget(self.mora_x_check_box)
        
    def __uncheck_two_mora(self):
        self.two_mora_check_box.setCheckState(Qt.Unchecked)
        
    def __uncheck_mora_x(self):
        self.mora_x_check_box.setCheckState(Qt.Unchecked)


class ReclistDetailLayout(QHBoxLayout):
    
    label: QLabel
    length_label: QLabel
    length_spin_box: QSpinBox
    cv_head_check_box: QCheckBox
    c_head_check_box: QCheckBox
    cv_mid_check_box: QCheckBox
    full_cv_check_box: QCheckBox
    
    def __init__(self) -> None:
        super().__init__()
        self.__init_layout()
        
    def __init_layout(self) -> None:
        self.label = QLabel('Reclist detail: ')
        self.length_label = QLabel('Length')
        self.length_spin_box = QSpinBox()
        self.length_spin_box.setRange(3, 50)
        self.cv_head_check_box = QCheckBox('CV head')
        self.c_head_check_box = QCheckBox('C head')
        self.cv_mid_check_box = QCheckBox('CV mid')
        self.full_cv_check_box = QCheckBox('Full CV')
        self.addWidget(self.label)
        self.addWidget(self.length_label)
        self.addWidget(self.length_spin_box)
        self.addWidget(self.cv_head_check_box)
        self.addWidget(self.c_head_check_box)
        self.addWidget(self.cv_mid_check_box)
        self.addWidget(self.full_cv_check_box)


class LabelStyleLayout(QHBoxLayout):
    
    label: QLabel
    bpm_label: QLabel
    blank_beat_label: QLabel
    bpm_spin_box: QSpinBox
    blank_beat: QSpinBox
    
    def __init__(self) -> None:
        super().__init__()
        self.__init_layout()
        
    def __init_layout(self) -> None:
        self.label = QLabel('Label Style: ')
        self.bpm_label = QLabel('Bpm')
        self.blank_beat_label = QLabel('Blank beat')
        self.bpm_spin_box = QSpinBox()
        self.bpm_spin_box.setRange(100, 200)
        self.bpm_spin_box.setSingleStep(10)
        self.blank_beat = QSpinBox()
        self.blank_beat.setRange(0, 10)
        self.blank_beat.setValue(2)
        self.addWidget(self.label)
        self.addWidget(self.bpm_spin_box)
        self.addWidget(self.bpm_label)
        self.addWidget(self.blank_beat)
        self.addWidget(self.blank_beat_label)


class SaveFileSpeciesLayout(QHBoxLayout):
    
    oto_check_box: QCheckBox
    presamp_check_box: QCheckBox
    vsdxmf_check_box: QCheckBox
    lsd_check_box: QCheckBox
    
    def __init__(self) -> None:
        super().__init__()
        self.__init_layout()
    
    def __init_layout(self) -> None:
        self.oto_check_box = QCheckBox('oto')
        self.presamp_check_box = QCheckBox('presamp')
        self.vsdxmf_check_box = QCheckBox('vsdxmf')
        self.lsd_check_box = QCheckBox('lsd')
        self.addWidget(self.oto_check_box)
        self.addWidget(self.presamp_check_box)
        self.addWidget(self.vsdxmf_check_box)
        self.addWidget(self.lsd_check_box)


class BottomButtonLayout(QHBoxLayout):
    
    preview_button: QPushButton
    save_button: QPushButton
    
    def __init__(self) -> None:
        super().__init__()
        self.__init_layout()
    
    def __init_layout(self) -> None:
        self.preview_button = QPushButton('Preview')
        self.save_button = QPushButton('Save')
        self.preview_button.setCheckable(True)
        self.save_button.setCheckable(True)
        self.addWidget(self.preview_button)
        self.addWidget(self.save_button)


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
    app = QApplication([])
    win = QMainWindow()
    widget = QWidget()
    layout = QVBoxLayout()
    layout1 = SelectDictFileLayout()
    layout2 = SelectSaveDirPath()
    layout.addLayout(layout1)
    layout.addLayout(layout2)
    widget.setLayout(layout)
    win.setCentralWidget(widget)
    win.show()
    app.exec()