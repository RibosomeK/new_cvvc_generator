from PySide6.QtGui import QUndoCommand, QUndoStack
from PySide6.QtWidgets import QLineEdit


class SelectFile(QUndoCommand):
    """a QUndoCommand that selects a file or directory"""
    
    file: str
    old_file: str
    line_edit: QLineEdit
    
    def undo(self) -> None:
        self.line_edit.setText(self.old_file)
        
    def redo(self) -> None:
        self.line_edit.setText(self.file)
        
        
class ClearCommand(QUndoCommand):
    """a QUndoCommand that clear selected files or directory"""
    
    