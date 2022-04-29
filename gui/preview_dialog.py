from PySide6.QtWidgets import QDialog
from .preview_dialog_ui import Ui_PreviewDialog


class PreviewDialog(QDialog, Ui_PreviewDialog):
    """a preview dialog in cvvc reclist generator."""
    
    def __init__(self):
        super().__init__()
        
        self.setupUi(self)