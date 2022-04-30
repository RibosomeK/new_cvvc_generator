from PySide6.QtGui import QUndoCommand
from PySide6.QtWidgets import QLineEdit
from .cvvc_reclist_generator_model import Parameters


class LineEditSetText(QUndoCommand):
    """a QUndoCommand that set lineEdit's text"""

    new_str: str
    old_str: str
    line_edit: QLineEdit

    def __init__(self, line_edit: QLineEdit, file: str):
        super().__init__()
        self.new_str = file
        self.old_str = line_edit.text()
        self.line_edit = line_edit

    def undo(self) -> None:
        self.line_edit.setText(self.old_str)

    def redo(self) -> None:
        self.line_edit.setText(self.new_str)


class LoadParametersCommand(QUndoCommand):
    """a QUndoCommand that can load config"""

    def __init__(self, new_parameters: Parameters, generator):
        super().__init__()
        self.new_parameters = new_parameters
        self.old_parameters = generator.parameters
        self.generator = generator

    def undo(self) -> None:
        self.generator.load_parameters(self.old_parameters)

    def redo(self) -> None:
        self.generator.load_parameters(self.new_parameters)


class ClearCommand(QUndoCommand):
    """a QUndoCommand that clear selected files or directory"""
