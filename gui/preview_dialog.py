# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preview_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.2.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QPushButton,
    QSizePolicy, QTabWidget, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_PreviewDialog(object):
    def setupUi(self, PreviewDialog):
        if not PreviewDialog.objectName():
            PreviewDialog.setObjectName(u"PreviewDialog")
        PreviewDialog.resize(592, 275)
        PreviewDialog.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.verticalLayout = QVBoxLayout(PreviewDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.preview_tab = QTabWidget(PreviewDialog)
        self.preview_tab.setObjectName(u"preview_tab")
        self.preview_tab.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.reclist_tab = QWidget()
        self.reclist_tab.setObjectName(u"reclist_tab")
        self.verticalLayout_3 = QVBoxLayout(self.reclist_tab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.reclist_textEdit = QTextEdit(self.reclist_tab)
        self.reclist_textEdit.setObjectName(u"reclist_textEdit")
        self.reclist_textEdit.setReadOnly(True)

        self.verticalLayout_3.addWidget(self.reclist_textEdit)

        self.preview_tab.addTab(self.reclist_tab, "")
        self.oto_tab = QWidget()
        self.oto_tab.setObjectName(u"oto_tab")
        self.verticalLayout_4 = QVBoxLayout(self.oto_tab)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.oto_textEdit = QTextEdit(self.oto_tab)
        self.oto_textEdit.setObjectName(u"oto_textEdit")
        self.oto_textEdit.setReadOnly(True)

        self.verticalLayout_4.addWidget(self.oto_textEdit)

        self.preview_tab.addTab(self.oto_tab, "")
        self.presamp_tab = QWidget()
        self.presamp_tab.setObjectName(u"presamp_tab")
        self.verticalLayout_5 = QVBoxLayout(self.presamp_tab)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.presamp_textEdit = QTextEdit(self.presamp_tab)
        self.presamp_textEdit.setObjectName(u"presamp_textEdit")
        self.presamp_textEdit.setReadOnly(True)

        self.verticalLayout_5.addWidget(self.presamp_textEdit)

        self.preview_tab.addTab(self.presamp_tab, "")
        self.vsdxmf_tab = QWidget()
        self.vsdxmf_tab.setObjectName(u"vsdxmf_tab")
        self.verticalLayout_6 = QVBoxLayout(self.vsdxmf_tab)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.vsdxmf_textEdit = QTextEdit(self.vsdxmf_tab)
        self.vsdxmf_textEdit.setObjectName(u"vsdxmf_textEdit")
        self.vsdxmf_textEdit.setReadOnly(True)

        self.verticalLayout_6.addWidget(self.vsdxmf_textEdit)

        self.preview_tab.addTab(self.vsdxmf_tab, "")
        self.lsd_tab = QWidget()
        self.lsd_tab.setObjectName(u"lsd_tab")
        self.verticalLayout_2 = QVBoxLayout(self.lsd_tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.lsd_textEdit = QTextEdit(self.lsd_tab)
        self.lsd_textEdit.setObjectName(u"lsd_textEdit")
        self.lsd_textEdit.setReadOnly(True)

        self.verticalLayout_2.addWidget(self.lsd_textEdit)

        self.preview_tab.addTab(self.lsd_tab, "")

        self.verticalLayout.addWidget(self.preview_tab)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.cancel_button = QPushButton(PreviewDialog)
        self.cancel_button.setObjectName(u"cancel_button")
        self.cancel_button.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.horizontalLayout.addWidget(self.cancel_button)

        self.save_button = QPushButton(PreviewDialog)
        self.save_button.setObjectName(u"save_button")
        self.save_button.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.horizontalLayout.addWidget(self.save_button)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(PreviewDialog)

        self.preview_tab.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(PreviewDialog)
    # setupUi

    def retranslateUi(self, PreviewDialog):
        PreviewDialog.setWindowTitle(QDialog.tr(u"Preview", None))
        self.preview_tab.setTabText(self.preview_tab.indexOf(self.reclist_tab), QDialog.tr(u"reclist", None))
        self.preview_tab.setTabText(self.preview_tab.indexOf(self.oto_tab), QDialog.tr(u"oto", None))
        self.preview_tab.setTabText(self.preview_tab.indexOf(self.presamp_tab), QDialog.tr(u"presamp", None))
        self.preview_tab.setTabText(self.preview_tab.indexOf(self.vsdxmf_tab), QDialog.tr(u"vsdxmf", None))
        self.preview_tab.setTabText(self.preview_tab.indexOf(self.lsd_tab), QDialog.tr(u"lsd", None))
        self.cancel_button.setText(QDialog.tr(u"Cancel", None))
#if QT_CONFIG(shortcut)
        self.cancel_button.setShortcut(QDialog.tr(u"Ctrl+C", None))
#endif // QT_CONFIG(shortcut)
        self.save_button.setText(QDialog.tr(u"Save", None))
#if QT_CONFIG(shortcut)
        self.save_button.setShortcut(QDialog.tr(u"Return", None))
#endif // QT_CONFIG(shortcut)
    # retranslateUi

