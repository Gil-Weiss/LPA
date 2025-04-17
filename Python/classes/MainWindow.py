import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout, QDialog, QMessageBox, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView)

#from Python.LPA_GUI import ROWS, COLS
from Python.classes.LPFEncoder import LPFEncoder
from Python.classes.WellButton import WellButton

ROWS, COLS = 4, 6

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LPA 24-Well Controller")
        self.layout = QVBoxLayout()

        self.grid = QGridLayout()
        self.wells = []

        for row in range(ROWS):
            for col in range(COLS):
                well = WellButton(row, col)
                self.grid.addWidget(well, row, col)
                self.wells.append(well)

        self.layout.addLayout(self.grid)

        btns = QHBoxLayout()
        export_csv = QPushButton("Export CSV")
        export_lpf = QPushButton("Export LPF")
        view_table = QPushButton("Show Table")

        export_csv.clicked.connect(self.export_csv)
        export_lpf.clicked.connect(self.export_lpf)
        view_table.clicked.connect(self.show_table)

        btns.addWidget(view_table)
        btns.addWidget(export_csv)
        btns.addWidget(export_lpf)
        self.layout.addLayout(btns)
        self.setLayout(self.layout)

    def collect_data(self):
        data = []
        for well in self.wells:
            if not well.active or well.config is None:
                continue
            for led in well.config:
                if led['on']:
                    data.append({
                        'Well': well.well_id,
                        'LED': led['color'],
                        **{k: led[k] for k in ('freq', 'high_intensity', 'low_intensity', 'duration', 'total_time', 'delay')}
                    })
        return data

    def show_table(self):
        data = self.collect_data()
        if not data:
            QMessageBox.warning(self, "Warning", "No LED configurations to show.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Well Configurations Table")
        layout = QVBoxLayout()
        table = QTableWidget()
        df = pd.DataFrame(data)

        table.setRowCount(len(df))
        table.setColumnCount(len(df.columns))
        table.setHorizontalHeaderLabels(df.columns)

        for i in range(len(df)):
            for j in range(len(df.columns)):
                table.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.exec_()

    def export_csv(self):
        data = self.collect_data()
        if not data:
            QMessageBox.warning(self, "Warning", "No LED configurations to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "config.csv", "CSV Files (*.csv)")
        if path:
            df = pd.DataFrame(data)
            df.to_csv(path, index=False)
            QMessageBox.information(self, "Saved", f"CSV saved to {path}")

    def export_lpf(self):
        data = self.collect_data()
        if not data:
            QMessageBox.warning(self, "Warning", "No LED configurations to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save LPF", "program.lpf", "LPF Files (*.lpf)")
        if not path:
            return

        try:
            numSteps = 5000
            timeStep = 1
            channelNum = 48
            gsVals = np.zeros((numSteps, 24, 2), dtype=np.uint16)
            for well in self.wells:
                if well.active and well.config:
                    for i, led in enumerate(well.config):
                        if led['on']:
                            period = 1000 / led['freq'] if led['freq'] > 0 else 1
                            high = int(led['high_intensity'] * 4096 / 100)
                            low = int(led['low_intensity'] * 4096 / 100)
                            for t in range(numSteps):
                                time = t * timeStep
                                if time < led['delay'] or time > led['total_time']:
                                    continue
                                if ((time - led['delay']) % period) < led['duration']:
                                    gsVals[t][well.well_id][i] = high
                                else:
                                    gsVals[t][well.well_id][i] = low
            LPFEncoder(gsVals, {
                'channelNum': channelNum,
                'timeStep': timeStep,
                'numSteps': numSteps
            }, path)
            QMessageBox.information(self, "Success", f"LPF saved to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))