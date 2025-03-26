import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QComboBox, QProgressBar, QListWidget, QMessageBox
from PyQt6.QtCore import Qt
from converter import Converter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LiteExport")
        self.setMinimumSize(600, 400)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        top_layout = QHBoxLayout()
        self.db_label = QLabel("No database selected")
        self.select_db_btn = QPushButton("Select Database")
        self.select_db_btn.clicked.connect(self.select_db)
        top_layout.addWidget(self.db_label)
        top_layout.addWidget(self.select_db_btn)
        layout.addLayout(top_layout)
        self.table_list = QListWidget()
        layout.addWidget(self.table_list)
        self.format_box = QComboBox()
        self.format_box.addItems(["txt", "csv", "json", "html"])
        layout.addWidget(self.format_box)
        self.output_label = QLabel("No output folder selected")
        self.select_out_btn = QPushButton("Select Output Folder")
        self.select_out_btn.clicked.connect(self.select_output)
        layout.addWidget(self.output_label)
        layout.addWidget(self.select_out_btn)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.clicked.connect(self.convert_tables)
        layout.addWidget(self.convert_btn)
        self.converter = None
        self.db_path = None
        self.output_folder = None

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
