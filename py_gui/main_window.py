import configparser
from .main_window_ui import Ui_MainWindow
from .undo_framework import LineEditSetText, LoadParametersCommand
from .pop_message_box import *
from .preview_dialog import PreviewDialog
from .cvvc_reclist_generator_model import Parameters, CvvcReclistGeneratorModel
from PySide6.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QApplication,
    QLineEdit,
    QCheckBox,
    QSpinBox,
)
from PySide6.QtGui import QUndoStack
from PySide6.QtCore import QTranslator, QEvent
import os


def read_parameters_config(config_path: str) -> Parameters:
    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")
    parameters = Parameters(
        dict_file=config["PARAMETERS"]["dict_file"],
        alias_config=config["PARAMETERS"]["alias_config"],
        redirect_config=config["PARAMETERS"]["redirect_config"],
        save_path=config["PARAMETERS"]["save_path"],
        is_two_mora=config["PARAMETERS"].getboolean("is_two_mora"),
        is_haru_style=config["PARAMETERS"].getboolean("is_haru_style"),
        is_mora_x=config["PARAMETERS"].getboolean("is_mora_x"),
        length=config["PARAMETERS"].getint("length"),
        is_full_cv=config["PARAMETERS"].getboolean("is_full_cv"),
        is_cv_head=config["PARAMETERS"].getboolean("is_cv_head"),
        is_c_head_4_utau=config["PARAMETERS"].getboolean("is_c_head_4_utau"),
        bpm=config["PARAMETERS"].getint("bpm"),
        blank_beat=config["PARAMETERS"].getint("blank_beat"),
        do_save_reclist=config["PARAMETERS"].getboolean("do_save_reclist"),
        do_save_oto=config["PARAMETERS"].getboolean("do_save_oto"),
        do_save_presamp=config["PARAMETERS"].getboolean("do_save_presamp"),
        do_save_vsdxmf=config["PARAMETERS"].getboolean("do_save_vsdxmf"),
        do_save_lsd=config["PARAMETERS"].getboolean("do_save_lsd"),
    )
    return parameters


class MainWindow(QMainWindow, Ui_MainWindow):
    """main window of the cvvc reclist generator."""

    def __init__(self, parameters: Parameters):
        super().__init__()

        self.setupUi(self)

        self.parameters = parameters
        self.setup_parameters()

        self.parameters_config_path: str = ""
        self.undo_stack = QUndoStack()

        self.trans = QTranslator(self)

        self.title = self.windowTitle()

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

        self.set_english_action.triggered.connect(self.to_en)
        self.set_simplified_chinese_action.triggered.connect(self.to_cn)
        self.set_japanese_action.triggered.connect(self.set_language)

        self.undo_action.triggered.connect(self.undo_stack.undo)
        self.redo_action.triggered.connect(self.undo_stack.redo)

        self.save_button.clicked.connect(self.save_files)
        
    def to_cn(self):
        """change language to cn"""
        print(self.trans.load("./scr_gui/translations/cn/zh-CN"))
        print(QApplication.instance().installTranslator(self.trans))
        self.retranslateUi(self)

    def to_en(self):
        """change language to en"""
        self.trans.load("")
        self.retranslateUi(self)

    def setup_parameters(self):
        """update parameters when changed"""
        self.dict_file_lineEdit.textChanged.connect(self._update_parameters)
        self.redirect_config_lineEdit.textChanged.connect(self._update_parameters)
        self.alias_config_lineEdit.textChanged.connect(self._update_parameters)
        self.save_path_lineEdit.textChanged.connect(self._update_parameters)

        self.two_mora_checkBox.stateChanged.connect(self._update_parameters)
        self.haru_style_checkBox.stateChanged.connect(self._update_parameters)
        self.mora_x_checkBox.stateChanged.connect(self._update_parameters)

        self.cv_head_checkBox.stateChanged.connect(self._update_parameters)
        self.full_cv_checkBox.stateChanged.connect(self._update_parameters)
        self.c_head_4_utau_checkBox.stateChanged.connect(self._update_parameters)

        self.reclist_checkBox.stateChanged.connect(self._update_parameters)
        self.presamp_checkBox.stateChanged.connect(self._update_parameters)
        self.oto_checkBox.stateChanged.connect(self._update_parameters)
        self.vsdxmf_checkBox.stateChanged.connect(self._update_parameters)
        self.lsd_checkBox.stateChanged.connect(self._update_parameters)

        self.length_spinBox.valueChanged.connect(self._update_parameters)
        self.bpm_spinBox.valueChanged.connect(self._update_parameters)
        self.blank_beat_spinBox.valueChanged.connect(self._update_parameters)

    def _update_parameters(self):
        """update slot"""
        sender = self.sender()
        if isinstance(sender, QLineEdit):
            self.parameters[sender.accessibleName()] = sender.text()
        elif isinstance(sender, QCheckBox):
            self.parameters[sender.accessibleName()] = sender.isChecked()
        elif isinstance(sender, QSpinBox):
            self.parameters[sender.accessibleName()] = sender.value()

    def select_dict_file(self):
        file_name = QFileDialog.getOpenFileName(
            self,
            self.tr("Select a dictionary file"),
            "./",
            self.tr("Dict file (*.txt);;Presamp file (*.ini);;LSD file (*.lsd)"),
        )[0]
        if file_name:
            # try to get relative path
            try:
                file_name: str = os.path.relpath(file_name)
            except ValueError:
                pass

            self.undo_stack.push(LineEditSetText(self.dict_file_lineEdit, file_name))
            self.dict_file_lineEdit.setText(file_name)

    def select_alias_config(self):
        file_name = QFileDialog.getOpenFileName(
            self,
            self.tr("Select an alias config"),
            "./",
            self.tr("Alias file (*.json)"),
        )[0]
        if file_name:
            # try to get relative path
            try:
                file_name: str = os.path.relpath(file_name)
            except ValueError:
                pass

            self.undo_stack.push(LineEditSetText(self.alias_config_lineEdit, file_name))
            self.alias_config_lineEdit.setText(file_name)

    def select_redirect_config(self):
        file_name = QFileDialog.getOpenFileName(
            self,
            self.tr("Select a redirect config"),
            "./",
            self.tr("Redirect file (*.ini)"),
        )[0]
        if file_name:
            # try to get relative path
            try:
                file_name: str = os.path.relpath(file_name)
            except ValueError:
                pass
            self.undo_stack.push(
                LineEditSetText(self.redirect_config_lineEdit, file_name)
            )
            self.redirect_config_lineEdit.setText(file_name)

    def select_save_path(self):
        path_name = QFileDialog.getExistingDirectory(
            self, self.tr("Select a save path"), "./"
        )
        if path_name:
            # try to get relative path
            try:
                path_name = os.path.relpath(path_name)
            except ValueError:
                pass
            self.undo_stack.push(LineEditSetText(self.save_path_lineEdit, path_name))
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
        if error_message := self.check_essential_parameter():
            pop_error_message_box(self.tr("Warning"), error_message)
        else:
            preview_dialog = PreviewDialog()
            parameters = self.parameters
            generator = CvvcReclistGeneratorModel(parameters)
            preview_dialog.receive_model(generator)

            preview_dialog.reclist_textEdit.setText(generator.get_reclist_str())
            preview_dialog.reclist_number_label.setText(
                self.tr(f"total lines: {len(generator.reclist_generator.reclist)}")
            )

            preview_dialog.oto_textEdit.setText(generator.get_oto_str())
            preview_dialog.oto_number_label.setText(
                self.tr(f"total lines: {len(generator.oto_generator.oto_union)}")
            )

            if parameters.do_save_presamp:
                preview_dialog.presamp_textEdit.setText(generator.get_presamp_str())

            preview_dialog.vsdxmf_textEdit.setText(generator.get_vsdxmf_str())
            preview_dialog.vsdxmf_number_label.setText(
                self.tr(f"total lines: {len(generator.vsdxmf_generator.vsdxmf_union)}")
            )

            if parameters.do_save_lsd:
                preview_dialog.lsd_textEdit.setText(generator.get_lsd_str())

            preview_dialog.exec()

    def check_essential_parameter(self) -> str | None:
        if not self.dict_file_lineEdit.text():
            return self.tr("Dictionary file is not selected.")

        if not (self.oto_checkBox.isChecked() or self.vsdxmf_checkBox.isChecked()):
            return self.tr("At least one label type is needed to be selected.")

    def export_parameters_config(self) -> None:
        """if current config file exist, overwrite it, otherwise save it."""

        config = configparser.ConfigParser()
        config["PARAMETERS"] = self.parameters.__dict__

        if not self.parameters_config_path:
            config_path = QFileDialog.getSaveFileName(
                self,
                self.tr("Select a save path"),
                "./config.ini",
                self.tr("Config file (*.ini)"),
            )[0]
        else:
            config_path = self.parameters_config_path

        config_name = config_path.split("/")[-1]
        self.setWindowTitle(f"{self.title} - {config_name}")

        if config_path:
            with open(config_path, mode="w", encoding="utf-8") as f:
                config.write(f)

    def load_parameters(self, parameters: Parameters) -> None:
        self.dict_file_lineEdit.setText(parameters.dict_file)
        self.redirect_config_lineEdit.setText(parameters.redirect_config)
        self.alias_config_lineEdit.setText(parameters.alias_config)
        self.save_path_lineEdit.setText(parameters.save_path)

        self.two_mora_checkBox.setChecked(parameters.is_two_mora)
        self.haru_style_checkBox.setChecked(parameters.is_haru_style)
        self.mora_x_checkBox.setChecked(parameters.is_mora_x)

        self.length_spinBox.setValue(parameters.length)
        self.full_cv_checkBox.setChecked(parameters.is_full_cv)
        self.cv_head_checkBox.setChecked(parameters.is_cv_head)
        self.c_head_4_utau_checkBox.setChecked(parameters.is_c_head_4_utau)

        self.bpm_spinBox.setValue(parameters.bpm)
        self.blank_beat_spinBox.setValue(parameters.blank_beat)

        self.reclist_checkBox.setChecked(parameters.do_save_reclist)
        self.oto_checkBox.setChecked(parameters.do_save_oto)
        self.presamp_checkBox.setChecked(parameters.do_save_presamp)
        self.vsdxmf_checkBox.setChecked(parameters.do_save_vsdxmf)
        self.lsd_checkBox.setChecked(parameters.do_save_lsd)

    def load_parameters_config(self):
        """read a parameters config and load it."""

        config_path = QFileDialog.getOpenFileName(
            self,
            self.tr("Select a parameters config"),
            "./",
            self.tr("Config file (*.ini)"),
        )[0]
        
        if not config_path:
            return
        
        self.parameters_config_path = config_path

        config_name = config_path.split("/")[-1]
        self.setWindowTitle(f"{self.windowTitle()} - {config_name}")

        parameters = read_parameters_config(config_path)
        self.undo_stack.push(LoadParametersCommand(parameters, self))
        self.load_parameters(parameters)

    def save_files(self):
        generator = CvvcReclistGeneratorModel(self.parameters)
        if self.parameters.do_save_reclist:
            generator.save_reclist()
        if self.parameters.do_save_oto:
            generator.save_oto()
        if self.parameters.do_save_presamp:
            generator.save_presamp()
        if self.parameters.do_save_vsdxmf:
            generator.save_vsdxmf()
        if self.parameters.do_save_lsd:
            generator.save_lsd()

        pop_success_message_box(self.tr("(>^ω^<)"), self.tr("Save successfully"))

    def set_language(self):
        """set language to reclist application"""
        self.trans.load("./scr_gui/translations/cn/zh-CN")
        QApplication.instance().installTranslator(self.trans)
        self.retranslateUi(self)
