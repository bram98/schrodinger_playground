# %%

import sys
import numpy as np
import os

os.environ["PYQTGRAPH_QT_LIB"] = "PyQt6"
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
    QSlider,
    QComboBox,
    QSizePolicy,
    QDoubleSpinBox,
    QCheckBox,
)
from PyQt6.QtCore import QSize, QTimer, Qt
import yaml

from wavefunctions import WavefunctionSelector
from potentials import PotentialSelector

from simulator import Simulator

# sys.exit()


class MainWindow(QMainWindow):
    param_control_settings = {
        "reim_scale": {"min": -200, "max": 200, "step": 1, "value": 0},
        "a": {"min": 0.05, "max": 0.5, "step": 0.05, "value": 0.45},
        "dt": {"min": 1e-7, "max": 0.1, "step": 1e-7, "value": 1e-6},
    }

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Schrödinger Playground")
        self.setMinimumSize(QSize(600, 500))

        align_top = Qt.AlignmentFlag.AlignTop

        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.setInterval(33)

        self.gl_plot = gl.GLViewWidget()

        layout = QHBoxLayout()
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar.setMinimumWidth(300)
        sidebar.setMaximumWidth(400)

        with open("./settings.yaml") as stream:
            try:
                settings = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print("Error: could not load settings.yaml. Using default")
                settings = dict(
                    dt=0.5e-2, N=200, m=1000, potential_inf_at=1000
                )

        self.sim = Simulator(
            dt=settings["dt"],
            N=settings["N"],
            potential=None,
            m=settings["m"],
            method="re_im_leapfrog",
            potential_inf_at=settings["potential_inf_at"],
        )

        self.gl_plot.setMinimumWidth(200)

        self.play_reset_layout = QHBoxLayout()
        self.play_button = QPushButton("")
        self.play_button.clicked.connect(self.set_play_state)
        self.play_button.setCheckable(True)
        self.play_button.setChecked(True)
        self.play_reset_layout.addWidget(
            self.play_button, 0, alignment=align_top
        )

        self.reset_button = QPushButton("reset")
        self.reset_button.clicked.connect(self.reset)
        self.play_reset_layout.addWidget(
            self.reset_button, 0, alignment=align_top
        )

        self.method_dropdown = QComboBox()
        self.method_dropdown.addItems(Simulator.methods)
        self.method_dropdown.currentTextChanged.connect(self.set_method)
        self.method_dropdown.currentTextChanged.emit(
            self.method_dropdown.currentText()
        )

        self.reim_scale = 1.0
        self.reim_scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.init_param_controls(
            self.reim_scale_slider, "reim_scale", self.set_reim_scale
        )

        self.init_plot2d(self.sim.x, self.sim.psi, self.sim.potential)
        self.init_plot3d(self.sim.x, self.sim.psi)

        self.energylabel = QLabel("")
        self.params_label = QLabel("")
        self.update_params_label()

        self.plot_toggle_layout = QHBoxLayout()
        self.plot3d_toggle = QCheckBox()
        self.plot3d_toggle.stateChanged.connect(self.toggle_plot3d)
        self.plot3d_toggle.setChecked(True)
        self.plot2d_toggle = QCheckBox()
        self.plot2d_toggle.stateChanged.connect(self.toggle_plot2d)
        self.plot2d_toggle.setChecked(True)

        self.add_with_label(
            self.plot_toggle_layout, self.plot3d_toggle, "3D plot"
        )

        self.add_with_label(
            self.plot_toggle_layout, self.plot2d_toggle, "2D plot"
        )

        self.wavefunction_selector = WavefunctionSelector()
        self.potential_selector = PotentialSelector()

        sidebar_layout.addLayout(self.play_reset_layout)
        # sidebar_layout.addLayout(self.parameters_layout)
        self.add_with_label(
            sidebar_layout,
            self.method_dropdown,
            "Method",
            stretch=1,
            alignment=align_top,
        )
        self.add_with_label(sidebar_layout, self.reim_scale_slider, "Scale")
        sidebar_layout.addWidget(
            self.wavefunction_selector, 0, alignment=align_top
        )
        sidebar_layout.addWidget(
            self.potential_selector, 0, alignment=align_top
        )
        sidebar_layout.addWidget(self.energylabel, 0, alignment=align_top)
        sidebar_layout.addWidget(self.params_label, 0, alignment=align_top)

        sidebar_layout.addLayout(self.plot_toggle_layout)

        sidebar_layout.addStretch()
        sidebar_layout.setSpacing(10)
        sidebar.setLayout(sidebar_layout)

        layout.addWidget(sidebar)
        layout.addWidget(self.gl_plot, stretch=1)
        layout.addWidget(self.plot2d, stretch=1)

        container = QWidget()
        container.setLayout(layout)

        # Set the central widget of the Window.
        self.setCentralWidget(container)

        # Start app when PyQt is ready
        QTimer.singleShot(0, self.start_simulation)

    def start_simulation(self):
        self.reset()
        self.set_play_state(True)

    def add_with_label(
        self,
        parent_layout,
        widget,
        label,
        layout_type=QHBoxLayout,
        label_kwargs={},
        **widget_kwargs,
    ):
        default_label_kwargs = dict(stretch=0)
        default_label_kwargs.update(label_kwargs)
        layout = layout_type()
        layout.setContentsMargins(0, 0, 0, 0)
        # layout.setSpacing(10)
        qlabel = QLabel(label)
        qlabel.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(qlabel, **default_label_kwargs)
        layout.addWidget(widget, **widget_kwargs)
        # container = QWidget()
        # container.setLayout(layout)
        parent_layout.addLayout(layout)

    def init_param_controls(
        self, control, param, changed_method, param_display=None
    ):
        if param_display is None:
            param_display = param
        control.valueChanged.connect(changed_method)
        sets = self.param_control_settings[param]
        control.setMinimum(sets["min"])
        control.setMaximum(sets["max"])
        control.setSingleStep(sets["step"])
        control.setValue(sets["value"])
        control.valueChanged.emit(control.value())

        return control

    def set_play_state(self, play):
        if play:
            self.timer.start()
            self.play_button.setText("Pause")
        else:
            self.timer.stop()
            self.play_button.setText("Play")

    def set_reim_scale(self, scale):
        self.reim_scale = 0.1 * 10 ** (scale / 100)

    def set_method(self, method):

        self.timer.stop()
        self.sim.method = method
        self.timer.start()

    def toggle_plot3d(self, enable):
        self.plot3d_enabled = enable
        if enable:
            self.gl_plot.show()
        else:
            self.gl_plot.hide()

    def toggle_plot2d(self, enable):
        self.plot2d_enabled = enable
        if enable:
            self.plot2d.show()
        else:
            self.plot2d.hide()

    def update_params_label(self):
        self.params_label.setText(
            f"m={self.sim.m:.0f}  hbar={self.sim.hbar:.1f}  dt={self.sim.dt:.1e}"
        )

    def reset(self):

        timer_running = self.timer.isActive()
        if timer_running:
            self.timer.stop()

        x = self.sim.x
        wavefunction = self.wavefunction_selector.get_wavefunction(x)
        self.sim.psi = wavefunction

        potential = self.potential_selector.get_potential(x)
        self.sim.potential = potential

        self.potential_line.setData(x, potential)

        self.update_params_label()

        if timer_running:
            self.timer.start()
        else:
            # this gets executed when the simulation is paused and reset is
            # pressed
            self.loop(0)

    def loop(self, physics_steps=10):
        for i in range(physics_steps):
            self.sim.step()
        energy = (
            np.vdot(
                self.sim.psi,
                self.sim.hamiltonian(self.sim.psi),
            ).real
            * self.sim.dx
        )
        self.energylabel.setText(f"Energy {energy:.6f}")
        if self.plot3d_enabled:
            self.update_plot3d()
        if self.plot2d_enabled:
            self.update_plot2d()

    def init_plot2d(self, x, psi, potential):
        # self.plot = pg.PlotWi
        # self.plot.plot(
        #     self.sim.x,
        #     self.sim.hamiltonian(self.sim.psi).real,
        # )
        # self.plot.setMinimumWidth(200)

        ######

        self.plot2d = pg.PlotWidget()
        self.plot2d.setMouseEnabled(x=False, y=True)
        self.plot2d.setYRange(-5, 5)

        axis_left = self.plot2d.getAxis("left")
        axis_left.setLabel("wavefunction")

        self.potential_view = pg.ViewBox()
        axis_right = self.plot2d.getAxis("right")
        axis_right.setPen("y")
        axis_right.setLabel("Potential")
        axis_right.setTextPen("y")
        axis_right.linkToView(self.potential_view)
        axis_right.show()

        self.plot2d.scene().addItem(self.potential_view)

        self.psi_2d_re = self.plot2d.plot(x, np.real(psi), pen="cyan")
        self.psi_2d_im = self.plot2d.plot(x, np.imag(psi), pen="magenta")
        self.psi_2d_abs = self.plot2d.plot(x, np.abs(psi))
        self.potential_line = pg.PlotDataItem(x, potential, pen="y")
        self.potential_view.addItem(self.potential_line)

        def update_views():
            self.potential_view.setGeometry(
                self.plot2d.getViewBox().sceneBoundingRect()
            )
            self.potential_view.linkedViewChanged(
                self.plot2d.getViewBox(), self.potential_view.XAxis
            )

        self.plot2d.getViewBox().sigRangeChanged.connect(update_views)

        # Call it once manually to align views at the start
        update_views()

    def update_plot2d(self):
        x = self.sim.x
        psi = self.sim.psi
        self.psi_2d_abs.setData(x, np.abs(psi))
        self.psi_2d_re.setData(x, np.real(psi))
        # self.psi_2d_re.setData(x, np.real(self.sim.kinetic))
        self.psi_2d_im.setData(x, np.imag(psi))
        # self.psi_2d_im.setData(x, np.real(self.sim.psi))

    def init_plot3d(self, x, psi):

        # Add a grid
        grid = gl.GLGridItem()
        grid.setSize(x=5, y=5, z=5)
        grid.setSpacing(x=0.5, y=0.5, z=0.5)
        self.gl_plot.addItem(grid)

        pts = np.array([x, np.real(psi), np.imag(psi)]).T

        # Create a line plot item and add it
        self.line_plot = gl.GLLinePlotItem(
            pos=pts, color=(1, 1, 1, 1), width=2, antialias=True
        )
        self.gl_plot.addItem(self.line_plot)

        # Set a default camera position
        self.gl_plot.setCameraPosition(distance=1.5)
        self.gl_plot.orbit(azim=240, elev=0)

    def update_plot3d(self):

        psi = self.sim.psi
        pts = np.array(
            [
                self.sim.x,
                np.real(psi) * self.reim_scale,
                np.imag(psi) * self.reim_scale,
            ]
        ).T
        self.line_plot.setData(pos=pts)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setStyleSheet("QWidget {border: 1px solid green; }") # For debugging layout
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
