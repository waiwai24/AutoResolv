
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
from PyQt5.QtWidgets import *

from libautoresolv.resultshower import ResultShower
from libautoresolv.util import *
from libautoresolv.error import *
from libautoresolv.dbcache import *
from libautoresolv.GUI.gui_export import GUI_EXPORT

export_windows = []

class GUI_MAIN(QtWidgets.QDialog):
    def __init__(self, cache):
        QtWidgets.QDialog.__init__(self, None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.cache = cache
        self.setupUi()
        self.setupAction()
        self.setupLabel()
        # Enable window close button
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, True)

    def setupUi(self):
        if not self.objectName():
            self.setObjectName(u"AutoResolv")
        self.resize(1200, 750)
        self.setMinimumSize(QSize(1000, 650))

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
            QCheckBox {
                spacing: 6px;
                color: #000000;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
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
            QLineEdit, QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 0px;
                padding: 4px;
                background-color: white;
                color: #000000;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #a0a0a0;
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QLabel {
                color: #000000;
            }
        """)

        # Main layout - vertical to stack top and bottom sections
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        # ========== TOP SECTION (Libraries Management & Library Search Paths) ==========
        top_section = QWidget()
        top_layout = QHBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(12)

        # Libraries Management Group (Left)
        self.libs_group = QGroupBox("Libraries Management")
        libs_layout = QVBoxLayout(self.libs_group)
        libs_layout.setContentsMargins(10, 15, 10, 10)
        libs_layout.setSpacing(6)

        self.lib_list = QListWidget()
        self.lib_list.setObjectName(u"lib_list")
        self.lib_list.setMinimumHeight(200)
        libs_layout.addWidget(self.lib_list)

        libs_layout.addWidget(QLabel("Select library to modify:"))

        self.combobox_lib = QComboBox()
        self.combobox_lib.setObjectName(u"combobox_lib")
        self.combobox_lib.setMinimumHeight(26)
        libs_layout.addWidget(self.combobox_lib)

        libs_layout.addWidget(QLabel("New library path:"))

        self.lineedit_lib = QLineEdit()
        self.lineedit_lib.setObjectName(u"lineedit_lib")
        self.lineedit_lib.setMinimumHeight(26)
        self.lineedit_lib.setPlaceholderText("Enter new library path...")
        libs_layout.addWidget(self.lineedit_lib)

        self.b_libchange = QPushButton("Change Library Path")
        self.b_libchange.setObjectName(u"b_libchange")
        self.b_libchange.setMinimumHeight(28)
        libs_layout.addWidget(self.b_libchange)

        top_layout.addWidget(self.libs_group)

        # Library Search Paths Group (Right)
        self.libpaths_group = QGroupBox("Library Search Paths")
        libpaths_layout = QVBoxLayout(self.libpaths_group)
        libpaths_layout.setContentsMargins(10, 15, 10, 10)
        libpaths_layout.setSpacing(6)

        self.libpath_list = QListWidget()
        self.libpath_list.setObjectName(u"libpath_list")
        self.libpath_list.setMinimumHeight(200)
        self.libpath_list.setContextMenuPolicy(Qt.CustomContextMenu)
        libpaths_layout.addWidget(self.libpath_list)

        libpaths_layout.addWidget(QLabel("Add new library search path:"))

        self.lineedit_lib_path = QLineEdit()
        self.lineedit_lib_path.setObjectName(u"lineedit_lib_path")
        self.lineedit_lib_path.setMinimumHeight(26)
        self.lineedit_lib_path.setPlaceholderText("Enter library directory path...")
        libpaths_layout.addWidget(self.lineedit_lib_path)

        self.b_libpathchange = QPushButton("Add Library Path")
        self.b_libpathchange.setObjectName(u"b_libpathchange")
        self.b_libpathchange.setMinimumHeight(28)
        libpaths_layout.addWidget(self.b_libpathchange)

        top_layout.addWidget(self.libpaths_group)

        # Set equal stretch for top section
        top_layout.setStretch(0, 1)
        top_layout.setStretch(1, 1)

        main_layout.addWidget(top_section)

        # ========== BOTTOM SECTION (All other controls) ==========
        bottom_section = QWidget()
        bottom_layout = QHBoxLayout(bottom_section)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(12)

        # Parameters Group
        params_group = QGroupBox("Active Parameters")
        params_layout = QVBoxLayout(params_group)
        params_layout.setContentsMargins(10, 15, 10, 10)
        params_layout.setSpacing(6)

        self.c_libc = QCheckBox("Resolve Libc functions")
        self.c_libc.setObjectName(u"c_libc")
        self.c_libc.setTristate(False)
        params_layout.addWidget(self.c_libc)

        self.c_demangle = QCheckBox("Demangle functions")
        self.c_demangle.setObjectName(u"c_demangle")
        self.c_demangle.setTristate(False)
        params_layout.addWidget(self.c_demangle)

        self.c_comment = QCheckBox("Comment IDA code")
        self.c_comment.setObjectName(u"c_comment")
        self.c_comment.setTristate(False)
        params_layout.addWidget(self.c_comment)

        self.c_verbose = QCheckBox("Verbose Mode")
        self.c_verbose.setObjectName(u"c_verbose")
        self.c_verbose.setTristate(False)
        params_layout.addWidget(self.c_verbose)

        bottom_layout.addWidget(params_group)

        # Information Group
        self.info_groupbox = QGroupBox("Information")
        self.info_groupbox.setObjectName(u"info_groupbox")

        self.info_layout = QFormLayout(self.info_groupbox)
        self.info_layout.setObjectName(u"info_layout")
        self.info_layout.setContentsMargins(10, 15, 10, 10)
        self.info_layout.setHorizontalSpacing(10)
        self.info_layout.setVerticalSpacing(8)

        self.l_info_db_path = QLabel("DB Cache Path:")
        self.l_info_db_path.setObjectName(u"l_info_db_path")

        self.v_info_db_path = QLabel()
        self.v_info_db_path.setObjectName(u"v_info_db_path")
        self.v_info_db_path.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.v_info_db_path.setWordWrap(True)
        self.v_info_db_path.setStyleSheet("QLabel { color: #505050; font-style: italic; }")

        self.l_info_db_value = QLabel("DB Contains Data:")
        self.l_info_db_value.setObjectName(u"l_info_db_value")

        self.v_info_db_value = QLabel()
        self.v_info_db_value.setObjectName(u"v_info_db_value")
        self.v_info_db_value.setStyleSheet("QLabel { color: #505050; font-style: italic; }")

        self.l_info_bin_path = QLabel("Binary Path:")
        self.l_info_bin_path.setObjectName(u"l_info_bin_path")

        self.v_info_bin_path = QLabel()
        self.v_info_bin_path.setObjectName(u"v_info_bin_path")
        self.v_info_bin_path.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.v_info_bin_path.setWordWrap(True)
        self.v_info_bin_path.setStyleSheet("QLabel { color: #505050; font-style: italic; }")

        self.info_layout.addRow(self.l_info_db_path, self.v_info_db_path)
        self.info_layout.addRow(self.l_info_db_value, self.v_info_db_value)
        self.info_layout.addRow(self.l_info_bin_path, self.v_info_bin_path)

        bottom_layout.addWidget(self.info_groupbox)

        # Actions & Operations Group (All buttons)
        actions_group = QGroupBox("Actions & Operations")
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setContentsMargins(10, 15, 10, 10)
        actions_layout.setSpacing(6)

        # First row: Resolve and Clean DB Cache
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(6)

        self.b_resolve = QPushButton("Resolve")
        self.b_resolve.setObjectName(u"b_resolve")
        self.b_resolve.setMinimumHeight(28)
        row1_layout.addWidget(self.b_resolve)

        self.b_cleandb = QPushButton("Clean DB Cache")
        self.b_cleandb.setObjectName(u"b_cleandb")
        self.b_cleandb.setMinimumHeight(28)
        row1_layout.addWidget(self.b_cleandb)

        actions_layout.addLayout(row1_layout)

        # Second row: Import and Export Signature
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(6)

        self.b_refactor_import = QPushButton("Import Signature")
        self.b_refactor_import.setObjectName(u"b_refactor_import")
        self.b_refactor_import.setMinimumHeight(28)
        row2_layout.addWidget(self.b_refactor_import)

        self.b_refactor_export = QPushButton("Export Signature")
        self.b_refactor_export.setObjectName(u"b_refactor_export")
        self.b_refactor_export.setMinimumHeight(28)
        row2_layout.addWidget(self.b_refactor_export)

        actions_layout.addLayout(row2_layout)

        bottom_layout.addWidget(actions_group)

        main_layout.addWidget(bottom_section)

        # Version label at very bottom
        self.label = QLabel("AutoResolv dev-v0.90p | Thibault Poncetta")
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("QLabel { color: #666; font-size: 9pt; }")
        main_layout.addWidget(self.label)

        self.retranslateUi()

        QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QCoreApplication.translate("AutoResolv", u"AutoResolv", None))


    def update_libs_count(self):
        """Update Libraries Management group title with count"""
        count = len(self.cache.libsinfo)
        self.libs_group.setTitle(f"Libraries Management ({count})")

    def update_paths_count(self):
        """Update Library Search Paths group title with count"""
        count = self.libpath_list.count()
        self.libpaths_group.setTitle(f"Library Search Paths ({count})")

    def setupLabel(self):
        # Set window title with binary name
        binary_name = idaapi.get_root_filename()
        self.setWindowTitle(f"AutoResolv - {binary_name}")

        # Set checkbox states from config
        self.c_comment.setChecked(self.cache.CONFIG['comment'])
        self.c_libc.setChecked(self.cache.CONFIG['libc'])
        self.c_demangle.setChecked(self.cache.CONFIG['demangle'])
        self.c_verbose.setChecked(self.cache.CONFIG['verbose'])

        # Populate library search paths with intelligent Windows path merging
        if len(self.cache.rpath) >= 1:
            i = 0
            while i < len(self.cache.rpath):
                path = self.cache.rpath[i]

                # Check if this is a single-character drive letter (Windows path split by colon)
                if len(path) == 1 and path.isalpha():
                    # Check if next path starts with backslash (incorrectly split Windows path)
                    if i + 1 < len(self.cache.rpath) and self.cache.rpath[i + 1].startswith('\\'):
                        # Merge drive letter with path: "W" + "\Final\..." -> "W:\Final\..."
                        merged_path = path + ':' + self.cache.rpath[i + 1]
                        normalized_path = os.path.normpath(merged_path)
                        self.libpath_list.addItem(normalized_path)
                        if self.cache.CONFIG.get('verbose', False):
                            print(f"[AutoResolv] Merged split Windows path: '{path}' + '{self.cache.rpath[i + 1]}' -> '{normalized_path}'")
                        i += 2  # Skip both the drive letter and the path part
                        continue
                    else:
                        # Single letter without following path - skip it
                        if self.cache.CONFIG.get('verbose', False):
                            print(f"[AutoResolv] Skipping orphaned drive letter: '{path}'")
                        i += 1
                        continue

                # Skip other invalid short paths
                if len(path) <= 2 and ':' not in path:
                    if self.cache.CONFIG.get('verbose', False):
                        print(f"[AutoResolv] Skipping invalid path fragment: '{path}'")
                    i += 1
                    continue

                # Normal path processing
                normalized_path = os.path.normpath(path)
                self.libpath_list.addItem(normalized_path)
                i += 1

        # Add default paths only on Linux
        import platform
        if platform.system() != 'Windows':
            self.libpath_list.addItem("/usr/lib/")
            self.libpath_list.addItem("/lib/x86_64-linux-gnu/")

        # Populate library list
        for lib in self.cache.libsinfo:
            # Normalize library path for display
            lib_path = os.path.normpath(self.cache.libsinfo[lib])
            self.lib_list.addItem(f"{lib} | {lib_path}")
            self.combobox_lib.addItem(lib)

        # Set information paths with tooltips
        self.v_info_db_path.setText(self.cache.db_path)
        self.v_info_db_path.setToolTip(f"Full path: {self.cache.db_path}")

        self.v_info_bin_path.setText(self.cache.bin_path)
        self.v_info_bin_path.setToolTip(f"Full path: {self.cache.bin_path}")

        # Set cache data status
        if self.cache.is_cached_data:
            self.v_info_db_value.setText("Yes")
            self.v_info_db_value.setStyleSheet("QLabel { color: #107c10; font-style: italic; font-weight: bold; }")
        else:
            self.v_info_db_value.setText("No")
            self.v_info_db_value.setStyleSheet("QLabel { color: #d13438; font-style: italic; font-weight: bold; }")

        # Update group titles with counts
        self.update_libs_count()
        self.update_paths_count()


    def setupAction(self):
        self.b_resolve.clicked.connect(self.on_button_resolv)
        self.c_comment.clicked.connect(self.on_parameter_modified)
        self.c_libc.clicked.connect(self.on_parameter_modified)
        self.c_demangle.clicked.connect(self.on_parameter_modified)
        self.c_verbose.clicked.connect(self.on_parameter_modified)
        self.combobox_lib.activated.connect(self.on_combox_event)
        self.b_cleandb.clicked.connect(self.on_button_cleandb)
        self.b_libchange.clicked.connect(self.on_button_libchange)

        self.b_refactor_export.clicked.connect(self.on_button_export)
        self.b_refactor_import.clicked.connect(self.on_button_import)
        self.b_libpathchange.clicked.connect(self.on_newlibpath)
        self.libpath_list.customContextMenuRequested.connect(self.show_libpath_context_menu)


    def on_button_export(self):
        try:
            print("[AutoResolv] ========== Export Signature File ==========")

            # Show dialog and check if user cancelled
            gui_export = GUI_EXPORT(self.cache)
            if gui_export.exec_() == QtWidgets.QDialog.Rejected:
                return

            # Check if database was selected
            if not hasattr(gui_export, 'exported_db'):
                print("[AutoResolv] ERROR: No database selected")
                return

            # Load main binary's cache
            main_db = os.path.join(self.cache.modpath, gui_export.exported_db)
            self.cache_extern = DB_CACHE_MANAGER(main_db, module_path=self.cache.modpath)

            if not self.cache_extern.check_cache_con():
                QtWidgets.QMessageBox.critical(self, "Export Error",
                    "Main binary cache is empty. Please run 'Resolve' on the main binary first!")
                return

            # Get resolved functions from main binary's cache
            self.cache_extern.parse_data_cache(no_check=True)
            values = self.cache_extern.cached_data

            if not values:
                QtWidgets.QMessageBox.critical(self, "Export Error",
                    "No resolved functions found in cache.\n\nPlease run 'Resolve' on the main binary first.")
                return

            # Extract signatures from current library
            print("[AutoResolv] Extracting function signatures...")
            cpt, allsig = getSignature(values, self.cache.CONFIG)

            if cpt == 0:
                QtWidgets.QMessageBox.warning(self, "Export Warning",
                    "No matching functions found!\n\nMake sure you opened the correct library file.")
                return

            # Save signatures
            self.cache_extern.save_signature(allsig)
            print(f"[AutoResolv] Successfully exported {cpt} function signatures")

            QtWidgets.QMessageBox.information(self, "Export Successful",
                f"Exported {cpt} function signatures!\n\nYou can now import them in the main binary.")
            print("[AutoResolv] ========== Export Complete ==========")

        except Exception as e:
            print(f"[AutoResolv] FATAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(self, "Export Error", f"Export failed:\n{str(e)}")
        
    

    def on_button_import(self):
        try:
            print("[AutoResolv] ========== Import Signature File ==========")

            if self.cache.CONFIG['verbose']:
                print("[AutoResolv] Importing Functions signature from cache")

            sigs = self.cache.parse_signature()
            if sigs is None:
                QtWidgets.QMessageBox.critical(self, "Import Error",
                    "No signature found!\n\nDid you use 'Export Signature' on the library file first?")
                return

            if self.cache.CONFIG['verbose']:
                print("[AutoResolv] Parsed cached successfully. Refactoring wrapper and XREF using signature")

            cpt, xref_cpt = refactorExtern(sigs, self.cache.CONFIG)

            if self.cache.CONFIG['verbose']:
                print(f"[AutoResolv] Successfully patched {cpt} functions and {xref_cpt} Xrefs")

            QtWidgets.QMessageBox.information(self, "Import Successful",
                f"Successfully imported signatures!\n\nPatched {cpt} functions and {xref_cpt} cross-references.")
            print("[AutoResolv] ========== Import Complete ==========")

        except Exception as e:
            print(f"[AutoResolv] FATAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(self, "Import Error", f"Import failed:\n{str(e)}")


    def on_button_cleandb(self):
        try:
            if hasattr(self.cache, 'close'):
                self.cache.close()
            os.remove(self.cache.db_path)
            if self.cache.CONFIG['verbose']:
                print("[AutoResolv] Cleaned DB Cache successful")
        except FileNotFoundError:
            if self.cache.CONFIG['verbose']:
                print("[AutoResolv] DB Cache file not found, assuming already cleaned")
        except PermissionError as e:
            if self.cache.CONFIG['verbose']:
                print(f"[AutoResolv] Failed to clean DB Cache: {str(e)}")
        except Exception as e:
            if self.cache.CONFIG['verbose']:
                print(f"[AutoResolv] Failed to clean DB Cache: {str(e)}")

        self.close()
        
        


    def on_newlibpath(self):
        newpath = self.lineedit_lib_path.text()
        if not newpath.endswith(os.sep):
            newpath += os.sep

        # Normalize path for consistency
        newpath = os.path.normpath(newpath)
        if not newpath.endswith(os.sep):
            newpath += os.sep

        foundNewLibrary = False
        self.cache.parse_libinfo_cache()
        for lib in self.cache.libsinfo:
            _exist = os.path.exists(os.path.join(newpath, lib))
            if (_exist):
                print(f"[AutoResolv] Librairy {lib} found !")
                lib_full_path = os.path.join(newpath, lib)
                self.cache.setNewLibPath(lib, lib_full_path, self.cache.CONFIG)
                items = self.lib_list.findItems(lib, QtCore.Qt.MatchContains)
                row = self.lib_list.row(items[0])
                self.lib_list.takeItem(row)
                # Normalize path for display
                normalized_lib_path = os.path.normpath(lib_full_path)
                self.lib_list.addItem(f"{lib} | {normalized_lib_path}")
                if not foundNewLibrary:
                    # Normalize path for display
                    normalized_newpath = os.path.normpath(newpath)
                    self.libpath_list.addItem(normalized_newpath)
                    self.cache.rpath.append(newpath)
                    self.cache.cache_save_rpath()

                foundNewLibrary = True

        if (not foundNewLibrary):
            raise Exception(f"[AutoResolv] Couldn't find any new library with path : {newpath}")

        self.cache.parse_libinfo_cache()
        if self.cache.CONFIG['verbose']:
            print("[AutoResolv] Updated cache and GUI")

        # Update counts in group titles
        self.update_libs_count()
        self.update_paths_count()


    def show_libpath_context_menu(self, position):
        """Show context menu for library search paths"""
        # Check if an item is selected
        item = self.libpath_list.itemAt(position)
        if item is None:
            return

        # Create context menu
        menu = QMenu(self)
        remove_action = menu.addAction("Remove Path")

        # Show menu and get selected action
        action = menu.exec_(self.libpath_list.mapToGlobal(position))

        # Execute action
        if action == remove_action:
            self.on_removelibpath()


    def on_removelibpath(self):
        """Remove selected library search path"""
        current_item = self.libpath_list.currentItem()

        # Check if an item is selected
        if current_item is None:
            QtWidgets.QMessageBox.warning(self, "No Selection",
                "Please select a library search path to remove.")
            return

        selected_path = current_item.text()

        # Confirm deletion
        reply = QtWidgets.QMessageBox.question(self, "Confirm Removal",
            f"Remove this library search path?\n\n{selected_path}",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.No:
            return

        # Try to remove from cache (it might not be in cache if it's a default path)
        try:
            # Normalize the path to match what might be in cache
            normalized_path = os.path.normpath(selected_path)

            # Try to find and remove from cache.rpath
            removed_from_cache = False
            for i, path in enumerate(self.cache.rpath):
                if os.path.normpath(path) == normalized_path:
                    self.cache.rpath.pop(i)
                    self.cache.cache_save_rpath()
                    removed_from_cache = True
                    if self.cache.CONFIG['verbose']:
                        print(f"[AutoResolv] Removed path from cache: {selected_path}")
                    break

            # Remove from list widget
            row = self.libpath_list.row(current_item)
            self.libpath_list.takeItem(row)

            # Update count
            self.update_paths_count()

            if self.cache.CONFIG['verbose']:
                if not removed_from_cache:
                    print(f"[AutoResolv] Removed path from UI only (not in cache): {selected_path}")
                else:
                    print("[AutoResolv] Updated cache and GUI")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Remove Error",
                f"Failed to remove path:\n{str(e)}")
            if self.cache.CONFIG['verbose']:
                print(f"[AutoResolv] Error removing path: {str(e)}")


    def on_button_libchange(self):
        current_lib = self.combobox_lib.currentText().replace(" ","")
        items = self.lib_list.findItems(current_lib, QtCore.Qt.MatchContains)
        old_path = None
        for item in items:
            old_path = item.text().split("|")[1].replace(" ","")

        new_path = self.lineedit_lib.text().replace(" ","")
        if self.cache.CONFIG['verbose']:
            print("[AutoResolv] Changing the path of {} :[{}] to [{}]".format(current_lib, old_path, new_path))

        self.cache.setNewLibPath(current_lib, new_path, self.cache.CONFIG)
        self.cache.parse_libinfo_cache()

        items = self.lib_list.findItems(current_lib, QtCore.Qt.MatchContains)
        row = self.lib_list.row(items[0])
        self.lib_list.takeItem(row)
        # Normalize path for display
        normalized_new_path = os.path.normpath(new_path)
        self.lib_list.addItem(f"{current_lib} | {normalized_new_path}")
        if self.cache.CONFIG['verbose']:
            print("[AutoResolv] Updated cache and GUI")

        # Update library count
        self.update_libs_count()   



    def on_button_resolv(self):
        try:
            if self.cache.is_cached_data:
                values = self.cache.cached_data
                if self.cache.CONFIG['verbose']:
                    print("[AutoResolv] Data found in DB Cache, not resolving again")

                rs = ResultShower("Result", values, self.cache.CONFIG['demangle'])
                r = rs.show()
                self.close()
                return

            if self.cache.CONFIG['verbose']:
                print("[AutoResolv] Looking for extern functions in .PLT | .PLT-SEC segment")                            
            start,end = get_seg(".plt")
            
            wrapper_funs_plt = {}
            wrapper_funs_plt2 = {}
            if start is not None and end is not None:
                wrapper_funs_plt = get_extern(start,end)
            
            start,end = get_seg(".plt.sec")
            if start is not None and end is not None:
                wrapper_funs_plt2 = get_extern(start,end)
         
            funs_binary = dict(wrapper_funs_plt)
            funs_binary.update(wrapper_funs_plt2)

            if len(funs_binary) == 0:
                raise IdaGetFunsError

            if self.cache.CONFIG['verbose']:
                print(f"[AutoResolv] Got {len(funs_binary)} functions")      

            total_libs = len(self.cache.libsinfo)
            self.progress = QProgressDialog("Parsing libraries...", "Cancel", 0, total_libs, self)
            self.progress.setWindowModality(Qt.WindowModal)
            self.progress.setAutoClose(False)  # Manual close for better control
            self.progress.setMinimumDuration(0)  # Show immediately
            self.progress.show()
            QCoreApplication.processEvents()  # Force initial display

            self.libsfun = {}
            for i, lib in enumerate(self.cache.libsinfo):
                # Update UI before processing
                self.progress.setLabelText(f"Parsing library: {lib} ({i+1}/{total_libs})")
                self.progress.setValue(i)
                QCoreApplication.processEvents()  # Refresh UI immediately

                if self.progress.wasCanceled():
                    self.progress.close()
                    return

                # Perform time-consuming operation
                funs = getAllFunsFromLib(self.cache.libsinfo[lib], self.cache.CONFIG['libc'])

                if funs is None:
                    if self.cache.CONFIG['verbose']:
                        print(f"[AutoResolv] Couldn't parse {lib}")
                    continue
                else:
                    if self.cache.CONFIG['verbose']:
                        print(f"[AutoResolv] Parsed {lib}")
                    self.libsfun[lib] = funs

                # Update progress after completion
                QCoreApplication.processEvents()  # Keep UI responsive

            self.progress.setValue(total_libs)
            QCoreApplication.processEvents()

            if self.cache.CONFIG['verbose']:
                print("\n[AutoResolv] All libs parsed. Resolving now...\n")

            # Show resolving phase with updated progress dialog
            self.progress.setLabelText("Resolving functions...")
            self.progress.setRange(0, 0)  # Indeterminate progress
            QCoreApplication.processEvents()

            values, external_resolved= Resolve(funs_binary, self.libsfun, self.cache.libsinfo, self.cache.CONFIG)

            # Close progress dialog after resolving
            self.progress.close()
            QCoreApplication.processEvents()  # Allow UI to refresh before showing results

            rs = ResultShower("Result", values, self.cache.CONFIG['demangle'])
            r = rs.show()

            if self.cache.CONFIG['comment']:
                if self.cache.CONFIG['verbose']:
                    print("[AutoResolv] Adding libname in IDA code near the call")
                CommentFuns(external_resolved, self.cache.CONFIG)
    
            self.cache.save_data(values, self.cache.CONFIG)
            if self.cache.CONFIG['verbose']:
                print("[AutoResolv] Data Saved to Cache")
                
            if self.cache.CONFIG['verbose']:
                print("[AutoResolv] All done ")

            self.close()
            
        except Exception as e:
            if hasattr(self, 'progress'):
                self.progress.close()
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def on_parameter_modified(self):
        self.cache.CONFIG['libc'] = self.c_libc.isChecked()
        self.cache.CONFIG['demangle'] = self.c_demangle.isChecked()
        self.cache.CONFIG['comment'] = self.c_comment.isChecked()
        self.cache.CONFIG['verbose'] = self.c_verbose.isChecked()

        self.cache.save_conf(self.cache.CONFIG)
        if self.cache.CONFIG['verbose']:
            print("[AutoResolv] Saved Active parameters to cache")

    def on_combox_event(self):
        text = self.combobox_lib.currentText()
        items = self.lib_list.findItems(text, QtCore.Qt.MatchContains)
        path = None
        for item in items:
            path = item.text().split("|")[1]
        self.lineedit_lib.setText(path)







        
