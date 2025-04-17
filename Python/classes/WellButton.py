import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QGridLayout, QLabel,
    QVBoxLayout, QHBoxLayout, QDialog, QCheckBox, QSpinBox, QDoubleSpinBox,
    QDialogButtonBox, QMessageBox, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView)

from PyQt5.QtGui import QPainter, QColor, QPen, QRegion
from PyQt5.QtCore import Qt, QRect
from matplotlib import pyplot as plt

#from Python.LPA_GUI import COLS
from Python.classes.WellConfigDialog import WellConfigDialog
ROWS, COLS = 4, 6

class WellButton(QPushButton):
    def __init__(self, row, col):
        super().__init__()
        self.row = row
        self.col = col
        self.well_id = row * COLS + col
        self.setFixedSize(80, 80)
        self.active = True
        self.config = [None, None]  # Red, Green LED config
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click)
        self.clicked.connect(self.left_click)
        self.update_ui()
        #self.setStyleSheet("border-radius: 40px; background-color: white; border: 2px solid black;")

    def update_ui(self):
        if not self.active:
            self.setText("X")
            self.setStyleSheet("background-color: lightgray; border-radius: 40px;")
        else:
            self.setText("")
            self.setStyleSheet("background-color: white; border-radius: 40px;")

    def right_click(self):
        self.active = not self.active
        self.update_ui()

    def left_click(self):
        if not self.active:
            return
        dialog = WellConfigDialog(self.well_id)
        if dialog.exec_():
            self.config = dialog.get_config()
            self.setStyleSheet("background-color: lightgreen; border-radius: 40px;")
            self.plot_preview()

    def plot_preview(self):
        fig, ax = plt.subplots()
        time = np.linspace(0, 5000, 5000)  # ms
        for led in self.config:
            if led['on']:
                period = 1000 / led['freq'] if led['freq'] > 0 else 1
                high = led['high_intensity'] * 4096 / 100
                low = led['low_intensity'] * 4096 / 100
                wave = np.where(((time - led['delay']) % period) < led['duration'], high, low)
                wave = np.where((time < led['delay']) | (time > led['total_time']), 0, wave)
                color = 'red' if led['color'] == 'Red' else 'green'
                ax.plot(time, wave, label=led['color'], color=color)
        ax.set_title(f"Well {self.well_id} Preview")
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Intensity")
        ax.legend()
        plt.show()
