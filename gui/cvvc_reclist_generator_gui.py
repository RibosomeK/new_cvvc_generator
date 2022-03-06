import configparser
from typing import Any

from cvvc_reclist_generator import vsdxmf_generator
from .main_window import Ui_MainWindow
from .preview_dialog import Ui_PreviewDialog
from PySide6.QtWidgets import QMainWindow, QFileDialog, QDialog, QMessageBox
from .cvvc_reclist_generator_model import Parameters, CvvcReclistGeneratorModel
from .label_highlighter import OtoHighlighter, VsdxmfHighlighter


class CvvcReclistGeneratorGui(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.parameters_config_path: str = ''
        
        self.dict_file_button.clicked.connect(self.select_dict_file)
        self.alias_config_button.clicked.connect(self.select_alias_config)
        self.redirect_config_button.clicked.connect(self.select_redirect_config)
        self.save_path_button.clicked.connect(self.select_save_path)
        
        self.two_mora_checkBox.stateChanged.connect(self.disable_mora_x_checkBox)
        self.mora_x_checkBox.stateChanged.connect(self.disable_two_mora_checkBox)
        
        self.preview_button.clicked.connect(self.pop_preview_dialog)
        
        self.export_action.triggered.connect(self.export_parameters_config)
        self.export_as_action.triggered.connect(self.export_parameters_config)
        self.load_action.triggered.connect(self.load_parameters_config)
        
        self.save_button.clicked.connect(self.save_files)
        
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
            parameters = self.get_parameters()
            generator = CvvcReclistGeneratorModel(parameters)
            preview_dialog.receive_model(generator)
            preview_dialog.reclist_textEdit.setText(generator.get_reclist_str())
            preview_dialog.oto_textEdit.setText(generator.get_oto_str())
            preview_dialog.presamp_textEdit.setText(generator.get_presamp_str())
            preview_dialog.vsdxmf_textEdit.setText(generator.get_vsdxmf_str())
            preview_dialog.lsd_textEdit.setText(generator.get_lsd_str())
            
            preview_dialog.exec()
        
    def check_essential_input(self) -> str | None:
        if not self.dict_file_lineEdit.text():
            return self.tr('Dictionary file is not selected.')
        
        if not (self.oto_checkBox.isChecked() or self.presamp_checkBox.isChecked() or
                self.vsdxmf_checkBox.isChecked() or self.lsd_checkBox.isChecked()):
            return self.tr('At least one dictionary type is not selected.')
        
    def get_parameters(self) -> Parameters:
        parameters = Parameters(
            dict_file=self.dict_file_lineEdit.text(),
            alias_config=self.alias_config_lineEdit.text(),
            redirect_config=self.redirect_config_lineEdit.text(),
            save_path=self.save_path_lineEdit.text(),
            
            is_two_mora=self.two_mora_checkBox.isChecked(),
            is_haru_style=self.haru_style_checkBox.isChecked(),
            is_mora_x=self.mora_x_checkBox.isChecked(),
            
            length=self.length_spinBox.value(),
            is_full_cv=self.full_cv_checkBox.isChecked(),
            is_cv_head=self.cv_head_checkBox.isChecked(),
            is_c_head=self.c_head_checkBox.isChecked(),
            cv_mid=self.cv_mid_lineEdit.text(),
            
            bpm=self.bpm_spinBox.value(),
            blank_beat=self.blank_beat_spinBox.value(),
            
            do_save_reclist=self.reclist_checkBox.isChecked(),
            do_save_oto=self.oto_checkBox.isChecked(),
            do_save_presamp=self.presamp_checkBox.isChecked(),
            do_save_vsdxmf=self.vsdxmf_checkBox.isChecked(),
            do_save_lsd=self.lsd_checkBox.isChecked()
        )
        return parameters
    
    def export_parameters_config(self) -> None:
        config = configparser.ConfigParser()
        config['PARAMETERS'] = self.get_parameters().__dict__
        
        if not self.parameters_config_path:
            config_path = QFileDialog.getSaveFileName(
                self,
                self.tr('Select a save path'), 
                './config.ini',
                self.tr('Config file (*.ini)')
            )[0]
        else:
            config_path = self.parameters_config_path
        
        if config_path:    
            with open(config_path, mode='w', encoding='utf-8') as f:
                config.write(f)
            
    def load_parameters_config(self) -> None:
        config_path = QFileDialog.getOpenFileName(
            self,
            self.tr('Select a parameters config'), 
            './',
            self.tr('Config file (*.ini)')
        )[0]
        self.parameters_config_path = config_path
        
        config_name = config_path.split('/')[-1]
        self.setWindowTitle(f'{self.windowTitle()} {config_name}')
        
        config = configparser.ConfigParser()
        config.read(config_path)
        self.dict_file_lineEdit.setText(config['PARAMETERS']['dict_file'])
        self.redirect_config_lineEdit.setText(config['PARAMETERS']['redirect_config'])
        self.alias_config_lineEdit.setText(config['PARAMETERS']['alias_config'])
        self.save_path_lineEdit.setText(config['PARAMETERS']['save_path'])
        
        self.two_mora_checkBox.setChecked(config['PARAMETERS'].getboolean('is_two_mora'))
        self.haru_style_checkBox.setChecked(config['PARAMETERS'].getboolean('is_haru_style'))
        self.mora_x_checkBox.setChecked(config['PARAMETERS'].getboolean('is_mora_x'))
            
        self.length_spinBox.setValue(config['PARAMETERS'].getint('length'))
        self.full_cv_checkBox.setChecked(config['PARAMETERS'].getboolean('is_full_cv'))
        self.cv_head_checkBox.setChecked(config['PARAMETERS'].getboolean('is_cv_head'))
        self.c_head_checkBox.setChecked(config['PARAMETERS'].getboolean('is_c_head'))
        self.cv_mid_lineEdit.setText(config['PARAMETERS']['cv_mid'])
            
        self.bpm_spinBox.setValue(config['PARAMETERS'].getint('bpm'))
        self.blank_beat_spinBox.setValue(config['PARAMETERS'].getint('blank_beat'))
            
        self.reclist_checkBox.setChecked(config['PARAMETERS'].getboolean('do_save_reclist'))
        self.oto_checkBox.setChecked(config['PARAMETERS'].getboolean('do_save_oto'))
        self.presamp_checkBox.setChecked(config['PARAMETERS'].getboolean('do_save_presamp'))
        self.vsdxmf_checkBox.setChecked(config['PARAMETERS'].getboolean('do_save_vsdxmf'))
        self.lsd_checkBox.setChecked(config['PARAMETERS'].getboolean('do_save_lsd'))
        
    def save_files(self):
        parameters = self.get_parameters()
        generator = CvvcReclistGeneratorModel(parameters)
        if parameters.do_save_reclist:
            generator.save_reclist()
        if parameters.do_save_oto:
            generator.save_oto()
        if parameters.do_save_presamp:
            generator.save_presamp()
        if parameters.do_save_vsdxmf:
            generator.save_vsdxmf()
        if parameters.do_save_lsd:
            generator.save_lsd()
            
        finish_message_box = QMessageBox()
        finish_message_box.setWindowTitle(self.tr('(>^ω^<)'))
        finish_message_box.setText(self.tr('Save successfully'))
        finish_message_box.exec()

class PreviewDialog(QDialog, Ui_PreviewDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.cancel_button.clicked.connect(self.close_dialog)
        self.save_button.clicked.connect(self.save_files)
        
        oto_highlighter = OtoHighlighter(self.oto_textEdit.document())
        vsdxmf_highligher = VsdxmfHighlighter(self.vsdxmf_textEdit.document())
        
        self.show()
        
    def close_dialog(self):
        self.close()
        
    def save_files(self):
        if self.generator.parameters.do_save_reclist:
            self.generator.save_reclist()
        if self.generator.parameters.do_save_oto:
            self.generator.save_oto()
        if self.generator.parameters.do_save_presamp:
            self.generator.save_presamp()
        if self.generator.parameters.do_save_vsdxmf:
            self.generator.save_vsdxmf()
        if self.generator.parameters.do_save_lsd:
            self.generator.save_lsd()
            
        finish_message_box = QMessageBox()
        finish_message_box.setWindowTitle(self.tr('(>^ω^<)'))
        finish_message_box.setText(self.tr('Save successfully'))
        finish_message_box.exec()
    
    def receive_model(self, generator: CvvcReclistGeneratorModel):
        self.generator = generator
    