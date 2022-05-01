# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preview_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.2.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QLocale, QMetaObject

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Ui_PreviewDialog(object):
    def setupUi(self, PreviewDialog):
        if not PreviewDialog.objectName():
            PreviewDialog.setObjectName("PreviewDialog")
        PreviewDialog.resize(592, 310)
        PreviewDialog.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.verticalLayout = QVBoxLayout(PreviewDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.preview_tab = QTabWidget(PreviewDialog)
        self.preview_tab.setObjectName("preview_tab")
        self.preview_tab.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.reclist_tab = QWidget()
        self.reclist_tab.setObjectName("reclist_tab")
        self.verticalLayout_3 = QVBoxLayout(self.reclist_tab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.reclist_textEdit = QTextEdit(self.reclist_tab)
        self.reclist_textEdit.setObjectName("reclist_textEdit")
        self.reclist_textEdit.setReadOnly(True)

        self.verticalLayout_3.addWidget(self.reclist_textEdit)

        self.reclist_number_label = QLabel(self.reclist_tab)
        self.reclist_number_label.setObjectName("reclist_number_label")

        self.verticalLayout_3.addWidget(self.reclist_number_label)

        self.preview_tab.addTab(self.reclist_tab, "")
        self.oto_tab = QWidget()
        self.oto_tab.setObjectName("oto_tab")
        self.verticalLayout_4 = QVBoxLayout(self.oto_tab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.oto_textEdit = QTextEdit(self.oto_tab)
        self.oto_textEdit.setObjectName("oto_textEdit")
        self.oto_textEdit.setReadOnly(True)

        self.verticalLayout_4.addWidget(self.oto_textEdit)

        self.oto_number_label = QLabel(self.oto_tab)
        self.oto_number_label.setObjectName("oto_number_label")

        self.verticalLayout_4.addWidget(self.oto_number_label)

        self.preview_tab.addTab(self.oto_tab, "")
        self.presamp_tab = QWidget()
        self.presamp_tab.setObjectName("presamp_tab")
        self.verticalLayout_5 = QVBoxLayout(self.presamp_tab)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.presamp_textEdit = QTextEdit(self.presamp_tab)
        self.presamp_textEdit.setObjectName("presamp_textEdit")
        self.presamp_textEdit.setReadOnly(True)

        self.verticalLayout_5.addWidget(self.presamp_textEdit)

        self.preview_tab.addTab(self.presamp_tab, "")
        self.vsdxmf_tab = QWidget()
        self.vsdxmf_tab.setObjectName("vsdxmf_tab")
        self.verticalLayout_6 = QVBoxLayout(self.vsdxmf_tab)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.vsdxmf_textEdit = QTextEdit(self.vsdxmf_tab)
        self.vsdxmf_textEdit.setObjectName("vsdxmf_textEdit")
        self.vsdxmf_textEdit.setReadOnly(True)

        self.verticalLayout_6.addWidget(self.vsdxmf_textEdit)

        self.vsdxmf_number_label = QLabel(self.vsdxmf_tab)
        self.vsdxmf_number_label.setObjectName("vsdxmf_number_label")

        self.verticalLayout_6.addWidget(self.vsdxmf_number_label)

        self.preview_tab.addTab(self.vsdxmf_tab, "")
        self.lsd_tab = QWidget()
        self.lsd_tab.setObjectName("lsd_tab")
        self.verticalLayout_2 = QVBoxLayout(self.lsd_tab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lsd_textEdit = QTextEdit(self.lsd_tab)
        self.lsd_textEdit.setObjectName("lsd_textEdit")
        self.lsd_textEdit.setReadOnly(True)

        self.verticalLayout_2.addWidget(self.lsd_textEdit)

        self.preview_tab.addTab(self.lsd_tab, "")

        self.verticalLayout.addWidget(self.preview_tab)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.cancel_button = QPushButton(PreviewDialog)
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.horizontalLayout.addWidget(self.cancel_button)

        self.save_button = QPushButton(PreviewDialog)
        self.save_button.setObjectName("save_button")
        self.save_button.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.horizontalLayout.addWidget(self.save_button)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(PreviewDialog)

        self.preview_tab.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(PreviewDialog)

    # setupUi

    def retranslateUi(self, PreviewDialog):
        PreviewDialog.setWindowTitle(QDialog.tr("Preview", None))
        self.reclist_number_label.setText(QDialog.tr("total lines: ", None))
        self.preview_tab.setTabText(
            self.preview_tab.indexOf(self.reclist_tab), QDialog.tr("reclist", None)
        )
        self.oto_number_label.setText(QDialog.tr("total lines: ", None))
        self.preview_tab.setTabText(
            self.preview_tab.indexOf(self.oto_tab), QDialog.tr("oto", None)
        )
        self.preview_tab.setTabText(
            self.preview_tab.indexOf(self.presamp_tab), QDialog.tr("presamp", None)
        )
        self.vsdxmf_number_label.setText(QDialog.tr("total lines: ", None))
        self.preview_tab.setTabText(
            self.preview_tab.indexOf(self.vsdxmf_tab), QDialog.tr("vsdxmf", None)
        )
        self.preview_tab.setTabText(
            self.preview_tab.indexOf(self.lsd_tab), QDialog.tr("lsd", None)
        )
        self.cancel_button.setText(QDialog.tr("Cancel", None))
        # if QT_CONFIG(shortcut)
        self.cancel_button.setShortcut(QDialog.tr("Ctrl+C", None))
        # endif // QT_CONFIG(shortcut)
        self.save_button.setText(QDialog.tr("Save", None))
        # if QT_CONFIG(shortcut)
        self.save_button.setShortcut(QDialog.tr("Return", None))


# endif // QT_CONFIG(shortcut)
# retranslateUi
