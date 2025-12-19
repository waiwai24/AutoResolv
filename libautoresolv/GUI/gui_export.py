
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

from libautoresolv.util import *
from libautoresolv.error import *
from libautoresolv.dbcache import *

class GUI_EXPORT(QtWidgets.QDialog):
    def __init__(self, cache):
        QtWidgets.QDialog.__init__(self, None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.cache = cache
        self.setupUi()
        self.setupAction()
        self.setup_label()
        # Enable window close button
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, True)


    def setupUi(self):
        if not self.objectName():
            self.setObjectName(u"Export")
        self.resize(900, 350)
        self.setMinimumSize(QSize(800, 300))

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
            QListWidget {
                border: 1px solid #d0d0d0;
                border-radius: 0px;
                background-color: white;
                alternate-background-color: #fafafa;
            }
            QListWidget::item:selected {
                background-color: #e0e0e0;
                color: #000000;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #000000;
            }
        """)

        # Create main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        # Left side - Cache list group
        left_group = QGroupBox("Available Cache Databases")
        left_layout = QVBoxLayout(left_group)
        left_layout.setContentsMargins(10, 12, 10, 10)

        self.listcache = QListWidget()
        self.listcache.setObjectName(u"listcache")
        self.listcache.setMinimumWidth(280)
        left_layout.addWidget(self.listcache)

        main_layout.addWidget(left_group)

        # Right side - Information and action group
        right_group = QGroupBox("Export Information")
        right_layout = QVBoxLayout(right_group)
        right_layout.setContentsMargins(10, 12, 10, 10)
        right_layout.setSpacing(8)

        # Info labels
        self.l_info = QLabel()
        self.l_info.setObjectName(u"l_info")
        self.l_info.setWordWrap(True)
        right_layout.addWidget(self.l_info)

        self.l_info2 = QLabel()
        self.l_info2.setObjectName(u"l_info2")
        self.l_info2.setWordWrap(True)
        self.l_info2.setStyleSheet("QLabel { color: #666; font-size: 10pt; }")
        right_layout.addWidget(self.l_info2)

        # Spacer
        right_layout.addSpacing(10)

        # Action section
        action_layout = QVBoxLayout()
        action_layout.setSpacing(6)

        self.l_cache_i = QLabel()
        self.l_cache_i.setObjectName(u"l_cache_i")
        action_layout.addWidget(self.l_cache_i)

        self.v_cache_i = QLabel()
        self.v_cache_i.setObjectName(u"v_cache_i")
        self.v_cache_i.setWordWrap(True)
        self.v_cache_i.setStyleSheet("QLabel { color: #2a7bde; font-style: italic; }")
        self.v_cache_i.setMinimumHeight(40)
        action_layout.addWidget(self.v_cache_i)

        right_layout.addLayout(action_layout)

        # Spacer to push button to bottom
        right_layout.addStretch()

        # Export button
        self.b_export = QPushButton()
        self.b_export.setObjectName(u"b_export")
        self.b_export.setMinimumHeight(28)
        right_layout.addWidget(self.b_export)

        main_layout.addWidget(right_group)

        # Set stretch factors (left:right = 1:2)
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 2)

        self.retranslateUi()

        QMetaObject.connectSlotsByName(self)
    # setupUi

    def retranslateUi(self):
        self.setWindowTitle(QCoreApplication.translate("Export", u"Export", None))
        self.b_export.setText(QCoreApplication.translate("Export", u"Export to Cache", None))
        self.l_info.setText(QCoreApplication.translate("Export", u"Please select the database cache of the main binary.", None))
        self.l_info2.setText(QCoreApplication.translate("Export", u"Note: AutoResolv will use the main binary cache to export only resolved functions.", None))
        self.l_cache_i.setText(QCoreApplication.translate("Export", u"Action:", None))
        self.v_cache_i.setText(QCoreApplication.translate("Export", u"", None))

    def setup_label(self):
        self.v_cache_i.setText("")
        cachelist = self.list_cache()

        # Get current binary name to filter it out
        current_binary = idaapi.get_root_filename()
        current_cache = f".cache_{current_binary}.db"

        # Set window title with binary name
        self.setWindowTitle(f"Export - {current_binary}")

        # Add cache files to list, excluding current library's cache
        added_count = 0
        for file in cachelist:
            if "No db found in" in file:
                self.listcache.addItem(file)
                added_count += 1
            elif file.endswith(".db"):
                # Skip current library's own cache
                if file != current_cache:
                    self.listcache.addItem(file)
                    added_count += 1

        if added_count == 0:
            self.listcache.addItem("No main binary cache found!")
            self.v_cache_i.setText("Please run 'Resolve' on the main binary first")
        else:
            self.v_cache_i.setText(f"Select main binary's cache to export signatures from {current_binary}")
        

    def setupAction(self):
        self.b_export.clicked.connect(self.on_button_export)
        self.listcache.itemClicked.connect(self.modify_action)

    def on_button_export(self):
        current_item = self.listcache.currentItem()
        if current_item is None:
            error_msg = "Please select a cache database from the list"
            QtWidgets.QMessageBox.warning(self, "No Selection", error_msg)
            return

        selected_db = current_item.text()

        if "No db found in" in selected_db or "No main binary cache found" in selected_db:
            error_msg = "Invalid selection. Please run 'Resolve' on the main binary first to create a cache database."
            QtWidgets.QMessageBox.critical(self, "Invalid Selection", error_msg)
            return

        self.exported_db = selected_db
        self.accept()  # Use accept() instead of close() to set dialog result to Accepted

    def list_cache(self):
        try:
            module_path = os.path.join(os.path.dirname(__file__), "..", "db") + os.sep

            if not os.path.exists(module_path):
                return [f"No db found in {module_path}"]

            db = os.listdir(module_path)
            return db
        except FileNotFoundError:
            return [f"No db found in {module_path}"]
        except Exception as e:
            return [f"Error listing cache: {str(e)}"]

    def modify_action(self):
        current_item = self.listcache.currentItem()
        if current_item is None:
            return

        selected_cache = current_item.text()
        current_binary = idaapi.get_root_filename()

        if "No db found in" in selected_cache or "No main binary cache found" in selected_cache:
            self.v_cache_i.setText("Invalid selection - no cache available")
        else:
            if selected_cache.startswith(".cache_") and selected_cache.endswith(".db"):
                main_binary_name = selected_cache[7:-3]
                self.v_cache_i.setText(f"Will export signatures from '{current_binary}' to '{main_binary_name}' cache")
            else:
                self.v_cache_i.setText(f"Will parse {selected_cache} and export {current_binary} signatures")
