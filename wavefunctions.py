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
    "sigma": {"min": 0.02, "max": 2, "step": 0.01, "value": 0.1},
    "momentum": {"min": -20, "max": 20, "step": 1.0, "value": 10},
    "n": {"min": 1, "max": 10, "step": 1, "value": 1},
    "n2": {"min": 1, "max": 10, "step": 1, "value": 2},
    "a": {"min": 0.05, "max": 0.5, "step": 0.05, "value": 0.45},
    "mu": {"min": -0.5, "max": 0.5, "step": 0.01, "value": 0.0},
}


class WavefunctionSelector(QWidget):
    names = ["wavepacket", "sine wave", "2 sine waves"]

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
        self.selector.addItems(WavefunctionSelector.names)
        self.selector.currentTextChanged.connect(self.pick_wavefunction)

        # self.controls = QWidget()
        self.controls_layout = QHBoxLayout()
        # self.controls.setLayout(self.controls_layout)
        # self.controls.setPalette(pal2)

        self.layout.addWidget(QLabel("Initial wavefunction"))
        self.layout.addWidget(self.selector)
        # self.layout.addWidget(self.controls)
        self.layout.addLayout(self.controls_layout)
        self.setLayout(self.layout)

        self.pick_wavefunction("wavepacket")

    def pick_wavefunction(self, text):

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

        if text == "wavepacket":
            nested_layout = QVBoxLayout()
            sigma_control = QDoubleSpinBox()
            self.init_param_controls(sigma_control, "sigma")

            momentum_control = QDoubleSpinBox()
            self.init_param_controls(momentum_control, "momentum")

            mu_control = QDoubleSpinBox()
            self.init_param_controls(mu_control, "mu")

            self.get_wavefunction = self.get_wavepacket

        elif text == "sine wave":
            n_control = QSpinBox()
            self.init_param_controls(n_control, "n")

            a_control = QDoubleSpinBox()
            self.init_param_controls(a_control, "a")

            self.get_wavefunction = self.get_sine

        elif text == "2 sine waves":
            n_control = QSpinBox()
            self.init_param_controls(n_control, "n")
            n2_control = QSpinBox()
            self.init_param_controls(n2_control, "n2")

            a_control = QDoubleSpinBox()
            self.init_param_controls(a_control, "a")

            self.get_wavefunction = self.get_2sines

    def save_param(self, param):
        def _save_param(value):
            self.params[param] = value

        return _save_param

    def get_wavepacket(self, x):
        sigma = self.params["sigma"]
        momentum = self.params["momentum"]
        mu = self.params["mu"]
        # This momentum is scaled incorrectly. It is really convenient that
        # integer momenta exactly fit inside the domain.
        psi = np.exp(-(x**2) / (2 * sigma**2) + 1j * x * 2 * np.pi * momentum)
        dx = x[1] - x[0]
        shift = mu / dx
        psi = np.roll(psi, shift)
        return psi

    def get_sine(self, x):
        n = self.params["n"]
        a = self.params["a"]
        return np.sin(np.pi * n * (x - a) / (2 * a))

    def get_2sines(self, x):
        n = self.params["n"]
        n2 = self.params["n2"]
        a = self.params["a"]
        return np.sin(np.pi * n * (x - a) / (2 * a)) + np.sin(
            np.pi * n2 * (x - a) / (2 * a)
        )

    def init_param_controls(
        self, control, param, param_display=None, layout=None
    ):
        if param_display is None:
            param_display = param
        control.valueChanged.connect(self.save_param(param))
        sets = param_control_settings[param]
        control.setMinimum(sets["min"])
        control.setMaximum(sets["max"])
        control.setSingleStep(sets["step"])
        control.setValue(sets["value"])
        control.valueChanged.emit(control.value())

        if layout is None:
            layout = self.controls_layout
        layout.addWidget(QLabel(param))
        layout.addWidget(control)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WavefunctionSelector()
    window.show()
    sys.exit(app.exec())
