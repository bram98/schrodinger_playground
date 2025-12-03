import sys
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
)

# from PyQt6 import Qt
from PyQt6.QtCore import QSize, QTimer, Qt
from PyQt6.QtGui import QPalette, QColor


param_control_settings = {
    "a": {"min": 0.05, "max": 0.5, "step": 0.05, "value": 0.45},
    "V0": {"min": 0, "max": 1000, "step": 0.05, "value": 2},
    "k": {"min": 0, "max": 5000, "step": 0.05, "value": 50},
}


class PotentialSelector(QWidget):
    names = [
        "zero potential",
        "infinite square well",
        "finite square well",
        "harmonic oscillator",
        "sine double well",
    ]

    def __init__(self):
        super().__init__()

        # pal = QPalette()
        # pal2 = QPalette()

        # // set black background
        # // Qt::black / "#000000" / "black"
        # pal.setColor(QPalette.ColorRole.Window, QColor("red"))
        # pal2.setColor(QPalette.ColorRole.Window, QColor("green"))

        # self.setAutoFillBackground(True)
        # self.setPalette(pal)

        self.layout = QVBoxLayout()

        self.params = dict()

        self.selector = QComboBox()
        self.selector.addItems(PotentialSelector.names)
        self.selector.currentTextChanged.connect(self.pick_potential)

        # self.controls = QWidget()
        self.controls_layout = QHBoxLayout()
        # self.controls.setLayout(self.controls_layout)
        # self.controls.setPalette(pal2)
        self.layout.addWidget(QLabel("Potential"))
        self.layout.addWidget(self.selector)
        # self.layout.addWidget(self.controls)
        self.layout.addLayout(self.controls_layout)
        self.setLayout(self.layout)

        self.pick_potential("zero potential")

    def pick_potential(self, text):

        self.params = dict()

        # delete old controls
        layout = self.controls_layout
        old_widgets = [
            layout.itemAt(i).widget() for i in range(layout.count())
        ]
        for old_widget in old_widgets:
            layout.removeWidget(old_widget)
            old_widget.deleteLater()
            old_widget = None

        names = [
            "zero potential",
            "infinite square well",
            "finite square well",
            "harmonic oscillator",
        ]
        if text == "zero potential":

            self.get_potential = self.get_zero_potential

        elif text == "infinite square well":
            a_control = QDoubleSpinBox()
            self.init_param_controls(a_control, "a")

            # self.controls_layout.addWidget(QLabel("a"))
            # self.controls_layout.addWidget(a_control)

            self.get_potential = self.get_infinite_square_well

        elif text == "finite square well":
            a_control = QDoubleSpinBox()
            self.init_param_controls(a_control, "a")

            V0_control = QDoubleSpinBox()
            self.init_param_controls(V0_control, "V0")

            # self.controls_layout.addWidget(QLabel("a"))
            # self.controls_layout.addWidget(a_control)
            # self.controls_layout.addWidget(QLabel("V0"))
            # self.controls_layout.addWidget(V0_control)

            self.get_potential = self.get_finite_square_well

        elif text == "harmonic oscillator":
            k_control = QDoubleSpinBox()
            self.init_param_controls(k_control, "k")

            self.get_potential = self.get_harmonic_oscillator

        elif text == "sine double well":
            V0_control = QDoubleSpinBox()
            self.init_param_controls(V0_control, "V0")

            self.get_potential = self.get_double_well_potential

    def save_param(self, param):
        def _save_param(value):
            self.params[param] = value

        return _save_param

    def init_param_controls(self, control, param, param_display=None):
        if param_display is None:
            param_display = param

        control.valueChanged.connect(self.save_param(param))
        sets = param_control_settings[param]
        control.setMinimum(sets["min"])
        control.setMaximum(sets["max"])
        control.setSingleStep(sets["step"])
        control.setValue(sets["value"])
        control.valueChanged.emit(control.value())

        self.controls_layout.addWidget(QLabel(param))
        self.controls_layout.addWidget(control)

    def get_zero_potential(self, x):
        return np.zeros_like(x)

    def get_infinite_square_well(self, x):
        a = self.params["a"]
        # pot = ((x > a) | (x < a)).astype(float) * 101.0
        # print(a)
        return ((x >= a) | (x <= -a)).astype(float) * 10001.0

    def get_finite_square_well(self, x):
        a = self.params["a"]
        V0 = self.params["V0"]
        return ((x >= a) | (x <= -a)).astype(float) * V0

    def get_harmonic_oscillator(self, x):
        k = self.params["k"]
        return 0.5 * k * x**2

    def get_double_well_potential(self, x):
        V0 = self.params["V0"]
        return V0 * (np.cos(4 * np.pi * x) + 1) / 2


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PotentialSelector()
    window.show()
    sys.exit(app.exec())
