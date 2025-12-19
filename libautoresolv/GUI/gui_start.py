
# This file is part of AutoResolv.
# Copyright 2022 - Airbus, thibault poncetta
# AutoResolv is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
# AutoResolv is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with AutoResolv.  If not, see <http://www.gnu.org/licenses/>.


import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
from PyQt5.QtWidgets import *
import idaapi


class GUI_START(QtWidgets.QDialog):
    def __init__(self, cpath):
        QtWidgets.QDialog.__init__(self, None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.cpath = cpath
        self.newpath = None
        self.setupUi()
        self.setupAction()
        self.setup_label()
        # Enable window close button
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, True)

    def setupUi(self):
        if not self.objectName():
            self.setObjectName(u"BinaryManagement")
        self.resize(700, 250)
        self.setMinimumSize(QSize(600, 200))

        # Apply IDA-style theme (clean white theme)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d0d0d0;
                border-radius: 0px;
                margin-top: 10px;
                padding-top: 8px;
                background-color: transparent;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
                color: #000000;
            }
            QPushButton {
                background-color: #f0f0f0;
                color: #000000;
                border: 1px solid #c0c0c0;
                border-radius: 0px;
                padding: 4px 10px;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #e5e5e5;
                border: 1px solid #b0b0b0;
            }
            QPushButton:pressed {
                background-color: #d8d8d8;
                border: 1px solid #a0a0a0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #b0b0b0;
                border: 1px solid #e0e0e0;
            }
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 0px;
                padding: 4px;
                background-color: white;
                color: #000000;
            }
            QLineEdit:focus {
                border: 1px solid #a0a0a0;
                background-color: #ffffff;
            }
            QLabel {
                color: #000000;
            }
        """)

        # Create main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Warning message at top
        self.l1 = QLabel()
        self.l1.setObjectName(u"l1")
        self.l1.setWordWrap(True)
        self.l1.setAlignment(Qt.AlignCenter)
        self.l1.setStyleSheet("QLabel { color: #c01c28; font-weight: bold; font-size: 11pt; }")
        main_layout.addWidget(self.l1)

        # Spacer
        main_layout.addSpacing(10)

        # Path input group
        path_group = QGroupBox("Binary Path Configuration")
        path_layout = QVBoxLayout(path_group)
        path_layout.setContentsMargins(10, 12, 10, 10)
        path_layout.setSpacing(6)

        # Current path label
        self.l2 = QLabel()
        self.l2.setObjectName(u"l2")
        path_layout.addWidget(self.l2)

        # Path input with browse button
        input_layout = QHBoxLayout()
        input_layout.setSpacing(6)

        self.textEdit = QLineEdit()
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setMinimumHeight(26)
        self.textEdit.setPlaceholderText("Enter or browse for binary path...")
        input_layout.addWidget(self.textEdit, 1)

        self.browseButton = QPushButton()
        self.browseButton.setObjectName(u"browseButton")
        self.browseButton.setMinimumWidth(80)
        self.browseButton.setMinimumHeight(26)
        input_layout.addWidget(self.browseButton)

        path_layout.addLayout(input_layout)

        main_layout.addWidget(path_group)

        # Spacer to push button to bottom
        main_layout.addStretch()

        # Confirm button
        self.pushButton = QPushButton()
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMinimumHeight(28)
        main_layout.addWidget(self.pushButton)

        self.retranslateUi()

        QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QCoreApplication.translate("BinaryManagement", u"Dialog", None))
        self.l1.setText(QCoreApplication.translate("BinaryManagement", u"⚠ Binary Project Not Found!\n\nThe IDB may have stored an old path, or the binary file has been moved.", None))
        self.l2.setText(QCoreApplication.translate("BinaryManagement", u"Current Path:", None))
        self.browseButton.setText(QCoreApplication.translate("BinaryManagement", u"Browse...", None))
        self.pushButton.setText(QCoreApplication.translate("BinaryManagement", u"Set New Binary Path", None))

    def setup_label(self):
        # Set window title with binary name
        binary_name = idaapi.get_root_filename()
        self.setWindowTitle(f"Binary Management - {binary_name}")

        self.textEdit.setText(self.cpath)

    def setupAction(self):
        self.pushButton.clicked.connect(self.onpathchange)
        self.browseButton.clicked.connect(self.onbrowse)

    def onbrowse(self):
        """Open file dialog to browse for binary file"""
        current_path = self.textEdit.text()

        # Set initial directory
        if current_path and os.path.exists(os.path.dirname(current_path)):
            initial_dir = os.path.dirname(current_path)
        else:
            initial_dir = os.path.expanduser("~")

        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Binary File",
            initial_dir,
            "All Files (*.*)"
        )

        # Update text field if user selected a file
        if file_path:
            self.textEdit.setText(file_path)

    def onpathchange(self):
        self.newpath = self.textEdit.text()
        self.close()
   
