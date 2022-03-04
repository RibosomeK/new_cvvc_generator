from warnings import warn
from .main_window import Ui_MainWindow
from .preview_dialog import Ui_PreviewDialog
from PySide6.QtWidgets import QMainWindow, QFileDialog, QDialog, QMessageBox

class CvvcReclistGeneratorGui(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.dict_file_button.clicked.connect(self.select_dict_file)
        self.alias_config_button.clicked.connect(self.select_alias_config)
        self.redirect_config_button.clicked.connect(self.select_redirect_config)
        self.save_path_button.clicked.connect(self.select_save_path)
        
        self.two_mora_checkBox.stateChanged.connect(self.disable_mora_x_checkBox)
        self.mora_x_checkBox.stateChanged.connect(self.disable_two_mora_checkBox)
        
        self.preview_button.clicked.connect(self.pop_preview_dialog)
        
        self.show()
        
    def select_dict_file(self):
        file_name = QFileDialog.getOpenFileName(
            self, self.tr('Select a dictionary file'), './',
            self.tr('Dict file (*.txt);;Presamp file (*.ini);;LSD file (*.lsd)'))[0]
        if file_name:
            self.dict_file_lineEdit.setText(file_name)
            
    def select_alias_config(self):
        file_name = QFileDialog.getOpenFileName(
            self, self.tr('Select an alias config'), './',
            self.tr('Alias file (*.ini)'))[0]
        if file_name:
            self.alias_config_lineEdit.setText(file_name)
            
    def select_redirect_config(self):
        file_name = QFileDialog.getOpenFileName(
            self, self.tr('Select a redirect config'), './',
            self.tr('Redirect file (*.ini)'))[0]
        if file_name:
            self.redirect_config_lineEdit.setText(file_name)
            
    def select_save_path(self):
        path_name = QFileDialog.getExistingDirectory(
            self, self.tr('Select a save path'), './')
        if path_name:
            self.save_path_lineEdit.setText(path_name)
            
    def disable_mora_x_checkBox(self):
        if self.two_mora_checkBox.isChecked():
            self.mora_x_checkBox.setEnabled(False)
        else:
            self.mora_x_checkBox.setEnabled(True)
            
    def disable_two_mora_checkBox(self):
        if self.mora_x_checkBox.isChecked():
            self.two_mora_checkBox.setEnabled(False)
        else:
            self.two_mora_checkBox.setEnabled(True)
            
    def pop_preview_dialog(self):
        if error_message := self.check_essential_input():
            warning_message_box = QMessageBox()
            warning_message_box.setWindowTitle(self.tr('Warning'))
            warning_message_box.setIcon(QMessageBox.Warning)
            warning_message_box.setText(error_message)
            warning_message_box.exec()
        else:
            preview_dialog = PreviewDialog()
            preview_dialog.exec()
        
    def check_essential_input(self) -> str | None:
        if not self.dict_file_lineEdit.text():
            return self.tr('Dictionary file is not selected.')
        

class PreviewDialog(QDialog, Ui_PreviewDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.cancel_button.clicked.connect(self.close_dialog)
        
        self.show()
        
    def close_dialog(self):
        self.close()