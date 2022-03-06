# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.2.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(415, 338)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.load_action = QAction(MainWindow)
        self.load_action.setObjectName(u"load_action")
        self.export_action = QAction(MainWindow)
        self.export_action.setObjectName(u"export_action")
        self.export_as_action = QAction(MainWindow)
        self.export_as_action.setObjectName(u"export_as_action")
        self.set_english_action = QAction(MainWindow)
        self.set_english_action.setObjectName(u"set_english_action")
        self.set_simplified_chinese_action = QAction(MainWindow)
        self.set_simplified_chinese_action.setObjectName(u"set_simplified_chinese_action")
        self.action = QAction(MainWindow)
        self.action.setObjectName(u"action")
        self.set_japanese_action = QAction(MainWindow)
        self.set_japanese_action.setObjectName(u"set_japanese_action")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.overall_layout = QVBoxLayout(self.centralwidget)
        self.overall_layout.setObjectName(u"overall_layout")
        self.dict_file_layout = QHBoxLayout()
        self.dict_file_layout.setObjectName(u"dict_file_layout")
        self.dict_file_label = QLabel(self.centralwidget)
        self.dict_file_label.setObjectName(u"dict_file_label")
        self.dict_file_label.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.dict_file_layout.addWidget(self.dict_file_label)

        self.dict_file_lineEdit = QLineEdit(self.centralwidget)
        self.dict_file_lineEdit.setObjectName(u"dict_file_lineEdit")
        self.dict_file_lineEdit.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.dict_file_lineEdit.setReadOnly(True)

        self.dict_file_layout.addWidget(self.dict_file_lineEdit)

        self.dict_file_button = QPushButton(self.centralwidget)
        self.dict_file_button.setObjectName(u"dict_file_button")
        self.dict_file_button.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.dict_file_button.setCheckable(False)

        self.dict_file_layout.addWidget(self.dict_file_button)


        self.overall_layout.addLayout(self.dict_file_layout)

        self.redirect_config_layout = QHBoxLayout()
        self.redirect_config_layout.setObjectName(u"redirect_config_layout")
        self.redirect_config_label = QLabel(self.centralwidget)
        self.redirect_config_label.setObjectName(u"redirect_config_label")
        self.redirect_config_label.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.redirect_config_layout.addWidget(self.redirect_config_label)

        self.redirect_config_lineEdit = QLineEdit(self.centralwidget)
        self.redirect_config_lineEdit.setObjectName(u"redirect_config_lineEdit")
        self.redirect_config_lineEdit.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.redirect_config_lineEdit.setReadOnly(True)

        self.redirect_config_layout.addWidget(self.redirect_config_lineEdit)

        self.redirect_config_button = QPushButton(self.centralwidget)
        self.redirect_config_button.setObjectName(u"redirect_config_button")
        self.redirect_config_button.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.redirect_config_button.setCheckable(False)

        self.redirect_config_layout.addWidget(self.redirect_config_button)


        self.overall_layout.addLayout(self.redirect_config_layout)

        self.alias_config_layout = QHBoxLayout()
        self.alias_config_layout.setObjectName(u"alias_config_layout")
        self.alias_config_label = QLabel(self.centralwidget)
        self.alias_config_label.setObjectName(u"alias_config_label")
        self.alias_config_label.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.alias_config_layout.addWidget(self.alias_config_label)

        self.alias_config_lineEdit = QLineEdit(self.centralwidget)
        self.alias_config_lineEdit.setObjectName(u"alias_config_lineEdit")
        self.alias_config_lineEdit.setEnabled(True)
        self.alias_config_lineEdit.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.alias_config_lineEdit.setReadOnly(True)

        self.alias_config_layout.addWidget(self.alias_config_lineEdit)

        self.alias_config_button = QPushButton(self.centralwidget)
        self.alias_config_button.setObjectName(u"alias_config_button")
        self.alias_config_button.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.alias_config_button.setCheckable(False)

        self.alias_config_layout.addWidget(self.alias_config_button)


        self.overall_layout.addLayout(self.alias_config_layout)

        self.reclist_style_layout = QHBoxLayout()
        self.reclist_style_layout.setObjectName(u"reclist_style_layout")
        self.reclist_style_label = QLabel(self.centralwidget)
        self.reclist_style_label.setObjectName(u"reclist_style_label")
        self.reclist_style_label.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.reclist_style_layout.addWidget(self.reclist_style_label)

        self.two_mora_checkBox = QCheckBox(self.centralwidget)
        self.two_mora_checkBox.setObjectName(u"two_mora_checkBox")
        self.two_mora_checkBox.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.reclist_style_layout.addWidget(self.two_mora_checkBox)

        self.haru_style_checkBox = QCheckBox(self.centralwidget)
        self.haru_style_checkBox.setObjectName(u"haru_style_checkBox")
        self.haru_style_checkBox.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.reclist_style_layout.addWidget(self.haru_style_checkBox)

        self.mora_x_checkBox = QCheckBox(self.centralwidget)
        self.mora_x_checkBox.setObjectName(u"mora_x_checkBox")
        self.mora_x_checkBox.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.reclist_style_layout.addWidget(self.mora_x_checkBox)


        self.overall_layout.addLayout(self.reclist_style_layout)

        self.reclist_detail_layout = QHBoxLayout()
        self.reclist_detail_layout.setObjectName(u"reclist_detail_layout")
        self.reclist_detail_label = QLabel(self.centralwidget)
        self.reclist_detail_label.setObjectName(u"reclist_detail_label")
        self.reclist_detail_label.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.reclist_detail_layout.addWidget(self.reclist_detail_label)

        self.reclist_detail_layout_a = QVBoxLayout()
        self.reclist_detail_layout_a.setObjectName(u"reclist_detail_layout_a")
        self.reclist_detail_layout_a1 = QHBoxLayout()
        self.reclist_detail_layout_a1.setObjectName(u"reclist_detail_layout_a1")
        self.length_spinBox = QSpinBox(self.centralwidget)
        self.length_spinBox.setObjectName(u"length_spinBox")
        self.length_spinBox.setMinimum(3)
        self.length_spinBox.setMaximum(100)

        self.reclist_detail_layout_a1.addWidget(self.length_spinBox)

        self.length_label = QLabel(self.centralwidget)
        self.length_label.setObjectName(u"length_label")

        self.reclist_detail_layout_a1.addWidget(self.length_label)

        self.cv_head_checkBox = QCheckBox(self.centralwidget)
        self.cv_head_checkBox.setObjectName(u"cv_head_checkBox")
        self.cv_head_checkBox.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.reclist_detail_layout_a1.addWidget(self.cv_head_checkBox)

        self.full_cv_checkBox = QCheckBox(self.centralwidget)
        self.full_cv_checkBox.setObjectName(u"full_cv_checkBox")
        self.full_cv_checkBox.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.full_cv_checkBox.setChecked(True)

        self.reclist_detail_layout_a1.addWidget(self.full_cv_checkBox)

        self.c_head_checkBox = QCheckBox(self.centralwidget)
        self.c_head_checkBox.setObjectName(u"c_head_checkBox")
        self.c_head_checkBox.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.reclist_detail_layout_a1.addWidget(self.c_head_checkBox)


        self.reclist_detail_layout_a.addLayout(self.reclist_detail_layout_a1)

        self.reclist_detail_layout_a2 = QHBoxLayout()
        self.reclist_detail_layout_a2.setObjectName(u"reclist_detail_layout_a2")
        self.cv_mid_label = QLabel(self.centralwidget)
        self.cv_mid_label.setObjectName(u"cv_mid_label")
        self.cv_mid_label.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.reclist_detail_layout_a2.addWidget(self.cv_mid_label)

        self.cv_mid_lineEdit = QLineEdit(self.centralwidget)
        self.cv_mid_lineEdit.setObjectName(u"cv_mid_lineEdit")
        self.cv_mid_lineEdit.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.reclist_detail_layout_a2.addWidget(self.cv_mid_lineEdit)


        self.reclist_detail_layout_a.addLayout(self.reclist_detail_layout_a2)


        self.reclist_detail_layout.addLayout(self.reclist_detail_layout_a)


        self.overall_layout.addLayout(self.reclist_detail_layout)

        self.labeling_style_layout = QHBoxLayout()
        self.labeling_style_layout.setObjectName(u"labeling_style_layout")
        self.labeling_style_label = QLabel(self.centralwidget)
        self.labeling_style_label.setObjectName(u"labeling_style_label")
        self.labeling_style_label.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.labeling_style_layout.addWidget(self.labeling_style_label)

        self.bpm_spinBox = QSpinBox(self.centralwidget)
        self.bpm_spinBox.setObjectName(u"bpm_spinBox")
        self.bpm_spinBox.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.bpm_spinBox.setMinimum(100)
        self.bpm_spinBox.setMaximum(200)
        self.bpm_spinBox.setSingleStep(10)
        self.bpm_spinBox.setValue(130)

        self.labeling_style_layout.addWidget(self.bpm_spinBox)

        self.bpm_label = QLabel(self.centralwidget)
        self.bpm_label.setObjectName(u"bpm_label")
        self.bpm_label.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.labeling_style_layout.addWidget(self.bpm_label)

        self.blank_beat_spinBox = QSpinBox(self.centralwidget)
        self.blank_beat_spinBox.setObjectName(u"blank_beat_spinBox")
        self.blank_beat_spinBox.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.blank_beat_spinBox.setMaximum(10)
        self.blank_beat_spinBox.setValue(2)

        self.labeling_style_layout.addWidget(self.blank_beat_spinBox)

        self.blank_beat_label = QLabel(self.centralwidget)
        self.blank_beat_label.setObjectName(u"blank_beat_label")
        self.blank_beat_label.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.labeling_style_layout.addWidget(self.blank_beat_label)


        self.overall_layout.addLayout(self.labeling_style_layout)

        self.save_path_layout = QHBoxLayout()
        self.save_path_layout.setObjectName(u"save_path_layout")
        self.save_path_label = QLabel(self.centralwidget)
        self.save_path_label.setObjectName(u"save_path_label")
        self.save_path_label.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.save_path_layout.addWidget(self.save_path_label)

        self.save_path_lineEdit = QLineEdit(self.centralwidget)
        self.save_path_lineEdit.setObjectName(u"save_path_lineEdit")
        self.save_path_lineEdit.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.save_path_lineEdit.setReadOnly(True)

        self.save_path_layout.addWidget(self.save_path_lineEdit)

        self.save_path_button = QPushButton(self.centralwidget)
        self.save_path_button.setObjectName(u"save_path_button")
        self.save_path_button.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.save_path_button.setCheckable(False)

        self.save_path_layout.addWidget(self.save_path_button)


        self.overall_layout.addLayout(self.save_path_layout)

        self.save_file_types_layout = QHBoxLayout()
        self.save_file_types_layout.setObjectName(u"save_file_types_layout")
        self.reclist_checkBox = QCheckBox(self.centralwidget)
        self.reclist_checkBox.setObjectName(u"reclist_checkBox")
        self.reclist_checkBox.setChecked(True)

        self.save_file_types_layout.addWidget(self.reclist_checkBox)

        self.oto_checkBox = QCheckBox(self.centralwidget)
        self.oto_checkBox.setObjectName(u"oto_checkBox")
        self.oto_checkBox.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.save_file_types_layout.addWidget(self.oto_checkBox)

        self.presamp_checkBox = QCheckBox(self.centralwidget)
        self.presamp_checkBox.setObjectName(u"presamp_checkBox")
        self.presamp_checkBox.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.save_file_types_layout.addWidget(self.presamp_checkBox)

        self.vsdxmf_checkBox = QCheckBox(self.centralwidget)
        self.vsdxmf_checkBox.setObjectName(u"vsdxmf_checkBox")
        self.vsdxmf_checkBox.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.save_file_types_layout.addWidget(self.vsdxmf_checkBox)

        self.lsd_checkBox = QCheckBox(self.centralwidget)
        self.lsd_checkBox.setObjectName(u"lsd_checkBox")
        self.lsd_checkBox.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.save_file_types_layout.addWidget(self.lsd_checkBox)


        self.overall_layout.addLayout(self.save_file_types_layout)

        self.bottom_button_layout = QHBoxLayout()
        self.bottom_button_layout.setObjectName(u"bottom_button_layout")
        self.preview_button = QPushButton(self.centralwidget)
        self.preview_button.setObjectName(u"preview_button")
        self.preview_button.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.preview_button.setCheckable(False)

        self.bottom_button_layout.addWidget(self.preview_button)

        self.save_button = QPushButton(self.centralwidget)
        self.save_button.setObjectName(u"save_button")
        self.save_button.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.save_button.setCheckable(False)

        self.bottom_button_layout.addWidget(self.save_button)


        self.overall_layout.addLayout(self.bottom_button_layout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 415, 22))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuSetting = QMenu(self.menuBar)
        self.menuSetting.setObjectName(u"menuSetting")
        self.menuLanguage = QMenu(self.menuSetting)
        self.menuLanguage.setObjectName(u"menuLanguage")
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuSetting.menuAction())
        self.menuFile.addAction(self.load_action)
        self.menuFile.addAction(self.export_action)
        self.menuFile.addAction(self.export_as_action)
        self.menuSetting.addAction(self.menuLanguage.menuAction())
        self.menuLanguage.addAction(self.set_english_action)
        self.menuLanguage.addAction(self.set_simplified_chinese_action)
        self.menuLanguage.addAction(self.set_japanese_action)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QMainWindow.tr(u"cvvc reclist generator", None))
        self.load_action.setText(QMainWindow.tr(u"Load", None))
#if QT_CONFIG(tooltip)
        self.load_action.setToolTip(QMainWindow.tr(u"Load", None))
#endif // QT_CONFIG(tooltip)
        self.export_action.setText(QMainWindow.tr(u"Export", None))
        self.export_as_action.setText(QMainWindow.tr(u"Export as ...", None))
        self.set_english_action.setText(QMainWindow.tr(u"English", None))
        self.set_simplified_chinese_action.setText(QMainWindow.tr(u"\u7b80\u4f53\u4e2d\u6587", None))
        self.action.setText(QMainWindow.tr(u"\u7e41\u9ad4\u4e2d\u6587\uff08\u81fa\u7063\uff09", None))
        self.set_japanese_action.setText(QMainWindow.tr(u"\u65e5\u672c\u8a9e", None))
        self.dict_file_label.setText(QMainWindow.tr(u"Dict file: ", None))
        self.dict_file_button.setText(QMainWindow.tr(u"Select", None))
        self.redirect_config_label.setText(QMainWindow.tr(u"Redirect config: ", None))
        self.redirect_config_button.setText(QMainWindow.tr(u"Select", None))
        self.alias_config_label.setText(QMainWindow.tr(u"Alias config: ", None))
        self.alias_config_button.setText(QMainWindow.tr(u"Select", None))
        self.reclist_style_label.setText(QMainWindow.tr(u"Reclist style: ", None))
        self.two_mora_checkBox.setText(QMainWindow.tr(u"2 mora", None))
        self.haru_style_checkBox.setText(QMainWindow.tr(u"Haru.J style", None))
        self.mora_x_checkBox.setText(QMainWindow.tr(u"mora x", None))
        self.reclist_detail_label.setText(QMainWindow.tr(u"Reclist detail: ", None))
        self.length_label.setText(QMainWindow.tr(u"Length", None))
        self.cv_head_checkBox.setText(QMainWindow.tr(u"CV head", None))
        self.full_cv_checkBox.setText(QMainWindow.tr(u"Full CV", None))
        self.c_head_checkBox.setText(QMainWindow.tr(u"C head", None))
        self.cv_mid_label.setText(QMainWindow.tr(u"CV mid", None))
        self.labeling_style_label.setText(QMainWindow.tr(u"Labeling style: ", None))
        self.bpm_label.setText(QMainWindow.tr(u"bpm", None))
        self.blank_beat_label.setText(QMainWindow.tr(u"blank beat", None))
        self.save_path_label.setText(QMainWindow.tr(u"Save path: ", None))
        self.save_path_lineEdit.setText(QMainWindow.tr(u"./result", None))
        self.save_path_button.setText(QMainWindow.tr(u"Select", None))
        self.reclist_checkBox.setText(QMainWindow.tr(u"reclist", None))
        self.oto_checkBox.setText(QMainWindow.tr(u"oto", None))
        self.presamp_checkBox.setText(QMainWindow.tr(u"presamp", None))
        self.vsdxmf_checkBox.setText(QMainWindow.tr(u"vsdxmf", None))
        self.lsd_checkBox.setText(QMainWindow.tr(u"lsd", None))
        self.preview_button.setText(QMainWindow.tr(u"Preview", None))
        self.save_button.setText(QMainWindow.tr(u"Save", None))
        self.menuFile.setTitle(QMainWindow.tr(u"File", None))
        self.menuSetting.setTitle(QMainWindow.tr(u"Setting", None))
        self.menuLanguage.setTitle(QMainWindow.tr(u"Language", None))
    # retranslateUi

