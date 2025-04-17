from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QGridLayout, QLabel,
    QVBoxLayout, QHBoxLayout, QDialog, QCheckBox, QSpinBox, QDoubleSpinBox,
    QDialogButtonBox, QMessageBox, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView)

class WellConfigDialog(QDialog):
    def __init__(self, well_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Well {well_id} - LED Configuration")
        self.well_id = well_id
        self.layout = QVBoxLayout()

        self.led_widgets = []
        self.led_colors = ["Red", "Green"]
        for led_color in self.led_colors:
            group = QVBoxLayout()
            label = QLabel(f"{led_color} LED")
            on_box = QCheckBox("On")
            freq = QDoubleSpinBox(); freq.setDecimals(2); freq.setSingleStep(0.1); freq.setMaximum(10000); freq.setPrefix("Freq: ")
            high_intensity = QSpinBox(); high_intensity.setMaximum(100); high_intensity.setPrefix("High (%): ")
            low_intensity = QSpinBox(); low_intensity.setMaximum(100); low_intensity.setPrefix("Low (%): ")
            duration = QSpinBox(); duration.setMaximum(10000); duration.setPrefix("Duration: ")
            total_time = QSpinBox(); total_time.setMaximum(100000); total_time.setPrefix("Total Time: ")
            delay = QSpinBox(); delay.setMaximum(100000); delay.setPrefix("Delay: ")

            group.addWidget(label)
            group.addWidget(on_box)
            group.addWidget(freq)
            group.addWidget(high_intensity)
            group.addWidget(low_intensity)
            group.addWidget(duration)
            group.addWidget(total_time)
            group.addWidget(delay)
            self.layout.addLayout(group)

            self.led_widgets.append({
                'color': led_color,
                'on': on_box, 'freq': freq,
                'high_intensity': high_intensity,
                'low_intensity': low_intensity,
                'duration': duration, 'total_time': total_time, 'delay': delay
            })

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def get_config(self):
        config = []
        for led in self.led_widgets:
            led_data = {
                'color': led['color'],
                'on': led['on'].isChecked(),
                'freq': led['freq'].value(),
                'high_intensity': led['high_intensity'].value(),
                'low_intensity': led['low_intensity'].value(),
                'duration': led['duration'].value(),
                'total_time': led['total_time'].value(),
                'delay': led['delay'].value()
            }
            config.append(led_data)
        return config
