from PySide6.QtWidgets import QDialog
from .preview_dialog_ui import Ui_PreviewDialog
from .label_highlighter import OtoHighlighter, VsdxmfHighlighter
from .pop_message_box import *
from .cvvc_reclist_generator_model import CvvcReclistGeneratorModel

import os
class PreviewDialog(QDialog, Ui_PreviewDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.cancel_button.clicked.connect(self.close)  # type: ignore
        self.save_button.clicked.connect(self.save_files)  # type: ignore

        oto_highlighter = OtoHighlighter(self.oto_textEdit.document())
        vsdxmf_highlighter = VsdxmfHighlighter(self.vsdxmf_textEdit.document())

    def save_files(self):
        
        if not os.path.exists(self.generator.parameters.save_path):
            os.mkdir(self.generator.parameters.save_path)
            
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

        pop_success_message_box(self.tr("(>^ω^<)"), self.tr("Save successfully"))  # type: ignore

    def receive_model(self, generator: CvvcReclistGeneratorModel):
        self.generator = generator
