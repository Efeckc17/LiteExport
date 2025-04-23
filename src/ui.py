import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QFileDialog, QLabel, QComboBox, 
                           QProgressBar, QListWidget, QMessageBox, QMenuBar,
                           QMenu, QAction, QStyleFactory)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from converter import Converter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LiteExport")
        self.setMinimumSize(800, 600)
        
        
        self.create_menu_bar()
        
        
        self.current_theme = "dark"
        self.apply_theme()
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)  
        layout.setContentsMargins(20, 20, 20, 20)
        
        
        db_group = QWidget()
        db_layout = QHBoxLayout(db_group)
        db_layout.setContentsMargins(0, 0, 0, 0)
        
        self.db_label = QLabel("No database selected")
        self.select_db_btn = QPushButton("Select Database")
        self.select_db_btn.setObjectName("select_db_btn") 
        self.select_db_btn.setToolTip("Select the SQLite database file to export from")
        self.select_db_btn.clicked.connect(self.select_db)
        db_layout.addWidget(self.db_label)
        db_layout.addWidget(self.select_db_btn)
        layout.addWidget(db_group)
        
        
        table_group = QWidget()
        table_layout = QVBoxLayout(table_group)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        table_label = QLabel("Select Tables to Export:")
        table_label.setToolTip("Select one or more tables to export (use Ctrl+Click for multiple selection)")
        self.table_list = QListWidget()
        self.table_list.setSelectionMode(QListWidget.MultiSelection)
        self.table_list.setToolTip("Select one or more tables to export (use Ctrl+Click for multiple selection)")
        table_layout.addWidget(table_label)
        table_layout.addWidget(self.table_list)
        layout.addWidget(table_group)
        
        
        format_group = QWidget()
        format_layout = QHBoxLayout(format_group)
        format_layout.setContentsMargins(0, 0, 0, 0)
        
        format_label = QLabel("Export Format:")
        format_label.setToolTip("Select the output format for the exported data")
        self.format_box = QComboBox()
        self.format_box.addItems(["txt", "csv", "json", "html"])
        self.format_box.setToolTip("Select the output format for the exported data")
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_box)
        layout.addWidget(format_group)
        
        
        output_group = QWidget()
        output_layout = QHBoxLayout(output_group)
        output_layout.setContentsMargins(0, 0, 0, 0)
        
        self.output_label = QLabel("No output folder selected")
        self.select_out_btn = QPushButton("Select Output Folder")
        self.select_out_btn.setObjectName("select_out_btn")  # For CSS styling
        self.select_out_btn.setToolTip("Select the folder where exported files will be saved")
        self.select_out_btn.clicked.connect(self.select_output)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.select_out_btn)
        layout.addWidget(output_group)
        
        
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setToolTip("Shows the progress of the current export operation")
        layout.addWidget(self.progress)
        
        
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.setObjectName("convert_btn")  
        self.convert_btn.setToolTip("Start the export process for selected tables")
        self.convert_btn.clicked.connect(self.convert_tables)
        self.convert_btn.setMinimumHeight(40)
        layout.addWidget(self.convert_btn)
        
        self.converter = None
        self.db_path = None
        self.output_folder = None

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        
        settings_menu = menubar.addMenu("Settings")
        
        
        theme_menu = settings_menu.addMenu("Theme")
        light_action = QAction("Light", self)
        light_action.triggered.connect(lambda: self.set_theme("light"))
        dark_action = QAction("Dark", self)
        dark_action.triggered.connect(lambda: self.set_theme("dark"))
        theme_menu.addAction(light_action)
        theme_menu.addAction(dark_action)

    def set_theme(self, theme):
        print(f"Setting theme to: {theme}")
        self.current_theme = theme
        self.apply_theme()

    def apply_theme(self):
        theme_file = os.path.join(os.path.dirname(__file__), "themes", f"{self.current_theme}.css")
        print(f"Loading theme from: {theme_file}")
        
        if os.path.exists(theme_file):
            try:
                with open(theme_file, "r", encoding='utf-8') as f:
                    style = f.read()
                    print(f"Style loaded successfully. Length: {len(style)}")
                    self.setStyleSheet(style)
                
                    self.update()
                    for widget in self.findChildren(QWidget):
                        widget.update()
            except Exception as e:
                print(f"Error loading theme: {str(e)}")
                QMessageBox.warning(self, "Theme Error", f"Could not load theme: {str(e)}")
        else:
            print(f"Theme file not found: {theme_file}")
            QMessageBox.warning(self, "Theme Error", f"Theme file not found: {theme_file}")

    def select_db(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select SQLite Database", "", "SQLite Files (*.db *.sqlite)")
        if path:
            self.db_path = path
            self.db_label.setText(os.path.basename(path))
            self.converter = Converter(path)
            self.table_list.clear()
            for t in self.converter.get_tables():
                self.table_list.addItem(t)

    def select_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.output_label.setText(folder)

    def convert_tables(self):
        if not self.db_path or not self.output_folder:
            QMessageBox.warning(self, "Warning", "Database or output folder not selected.")
            return
        items = self.table_list.selectedItems()
        if not items:
            QMessageBox.warning(self, "Warning", "No table selected.")
            return
        fmt = self.format_box.currentText()
        for i in items:
            self.progress.setValue(0)
            table_name = i.text()
            self.converter.convert(table_name, fmt, self.output_folder, self.update_progress)
        QMessageBox.information(self, "Done", "Conversion completed.")

    def update_progress(self, val):
        self.progress.setValue(val)
