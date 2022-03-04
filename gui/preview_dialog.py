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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QListView,
    QPushButton, QSizePolicy, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_PreviewDialog(object):
    def setupUi(self, PreviewDialog):
        if not PreviewDialog.objectName():
            PreviewDialog.setObjectName(u"PreviewDialog")
        PreviewDialog.resize(413, 357)
        PreviewDialog.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.verticalLayout = QVBoxLayout(PreviewDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.preview_tab = QTabWidget(PreviewDialog)
        self.preview_tab.setObjectName(u"preview_tab")
        self.preview_tab.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.oto_tab = QWidget()
        self.oto_tab.setObjectName(u"oto_tab")
        self.horizontalLayout_2 = QHBoxLayout(self.oto_tab)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.oto_listView = QListView(self.oto_tab)
        self.oto_listView.setObjectName(u"oto_listView")

        self.horizontalLayout_2.addWidget(self.oto_listView)

        self.preview_tab.addTab(self.oto_tab, "")
        self.presamp_tab = QWidget()
        self.presamp_tab.setObjectName(u"presamp_tab")
        self.horizontalLayout_3 = QHBoxLayout(self.presamp_tab)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.presamp_listView = QListView(self.presamp_tab)
        self.presamp_listView.setObjectName(u"presamp_listView")

        self.horizontalLayout_3.addWidget(self.presamp_listView)

        self.preview_tab.addTab(self.presamp_tab, "")
        self.vsdxmf_tab = QWidget()
        self.vsdxmf_tab.setObjectName(u"vsdxmf_tab")
        self.horizontalLayout_4 = QHBoxLayout(self.vsdxmf_tab)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.vsdxmf_listView = QListView(self.vsdxmf_tab)
        self.vsdxmf_listView.setObjectName(u"vsdxmf_listView")

        self.horizontalLayout_4.addWidget(self.vsdxmf_listView)

        self.preview_tab.addTab(self.vsdxmf_tab, "")
        self.lsd_tab = QWidget()
        self.lsd_tab.setObjectName(u"lsd_tab")
        self.verticalLayout_2 = QVBoxLayout(self.lsd_tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.lsd_listView = QListView(self.lsd_tab)
        self.lsd_listView.setObjectName(u"lsd_listView")

        self.verticalLayout_2.addWidget(self.lsd_listView)

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
        self.preview_tab.setTabText(self.preview_tab.indexOf(self.oto_tab), QDialog.tr(u"oto", None))
        self.preview_tab.setTabText(self.preview_tab.indexOf(self.presamp_tab), QDialog.tr(u"presamp", None))
        self.preview_tab.setTabText(self.preview_tab.indexOf(self.vsdxmf_tab), QDialog.tr(u"vsdxmf", None))
        self.preview_tab.setTabText(self.preview_tab.indexOf(self.lsd_tab), QDialog.tr(u"lsd", None))
        self.cancel_button.setText(QDialog.tr(u"Cancel", None))
        self.save_button.setText(QDialog.tr(u"Save", None))
    # retranslateUi

