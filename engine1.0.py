# ————————————————————————————————————————————————————————————————
# HOMOGENIZER GUI — PyQt5-Based Physics-Driven Interface
# Includes Navbar and Home Screen by PhyzTech
# ————————————————————————————————————————————————————————————————

import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QPushButton, QDoubleSpinBox, QGridLayout, QTabWidget,
    QStackedWidget, QListWidget, QListWidgetItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QLinearGradient, QColor, QBrush, QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QRadialGradient
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QRadialGradient
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QRectF

# ————————————————————————————————— CLASS: Physics Engine —————————————————————————————————
class HomogenizerPhysics:
    def __init__(self, A, f, m, mu, R0, R_target, d, alpha=0.8):
        self.A = A                # Amplitude [m]
        self.f = f                # Frequency [Hz]
        self.m = m                # Bead mass [kg]
        self.mu = mu              # Fluid viscosity [Pa.s]
        self.R0 = R0              # Initial globule size [um]
        self.R_target = R_target  # Target globule size [um]
        self.d = d                # Tube diameter [m]
        self.alpha = alpha        # Empirical constant
        self.omega = 2 * np.pi * f

    def vmax(self):
        return self.A * self.omega

    def Ek(self):
        return 0.5 * self.m * (self.vmax())**2

    def shear_rate(self):
        return self.vmax() / self.d

    def kd(self):
        return self.alpha * self.f * self.Ek() / self.mu

    def time_to_target(self):
        return (1 / self.kd()) * np.log(self.R0 / self.R_target)

    def decay_curve(self, t):
        return self.R0 * np.exp(-self.kd() * t)


# ———————————————————————————————— CLASS: Plot Widget —————————————————————————————————
class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig, self.ax = plt.subplots(figsize=(6, 4))
        super().__init__(fig)
        self.setParent(parent)

    def plot_decay(self, model):
        self.ax.clear()
        t = np.linspace(0, model.time_to_target() * 1.2, 300)
        R = model.decay_curve(t)
        self.ax.plot(t, R, label="Globule Size R(t)")
        self.ax.axhline(model.R_target, linestyle='--', color='gray', label="Target")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Globule Size (µm)")
        self.ax.set_title("Globule Decay Over Time")
        self.ax.legend()
        self.draw()


# ——————————————————————————— CLASS: Main Input/Simulation Screen ———————————————————————————
class HomogenizerSimulationScreen(QWidget):
    def __init__(self):
        super().__init__()
        outer_layout = QVBoxLayout()  # <-- this will hold the title and main box

        # Title goes here
        title = QLabel("Simulation")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet("""
            background-color: #3c3f42;
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            margin-bottom: 10px;
        """)
        outer_layout.addWidget(title)  # <-- This adds the big SIMULATION title at the top

        # Now the main frame for content
        main_frame = QWidget()
        main_frame.setStyleSheet("""
            background-color: #2a2d30;
            border-radius: 10px;
            padding: 15px;
        """)
        layout = QHBoxLayout()
        main_frame.setLayout(layout)

        # Add your control panel and plot here, as before
        # control_layout = QVBoxLayout() ...
        # layout.addLayout(control_layout, 1)
        # layout.addWidget(self.plot, 2)

        outer_layout.addWidget(main_frame)  # <-- This adds your full simulation panel
        self.setLayout(outer_layout)        # <-- Apply the layout to the screen
        control_layout = QVBoxLayout()
        self.plot = PlotCanvas(self)

        # Grid for inputs
        grid = QGridLayout()
        self.spinboxes = {}
        labels = [
            ("Amplitude A (mm)", 1),
            ("Frequency f (Hz)", 20),
            ("Bead Mass m (g)", 1),
            ("Viscosity µ (Pa·s)", 0.001),
            ("Initial Size R₀ (µm)", 100),
            ("Target Size Rₜ (µm)", 10),
            ("Tube Diameter d (mm)", 10),
        ]

        for i, (label, default) in enumerate(labels):
            grid.addWidget(QLabel(label), i, 0)

            box = QDoubleSpinBox()
            box.setRange(0.0001, 100000)
            box.setDecimals(4)
            box.setValue(default)

            # 🎯 Apply white-arrow styling here
            box.setStyleSheet("""
    QDoubleSpinBox {
        color: white;
        background-color: #2a2d30;
        border: 1px solid #3c3f42;
        border-radius: 4px;
        padding-right: 20px; /* Leave space for arrows */
    }

    QDoubleSpinBox::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 16px;
        height: 12px;
        border: none;
        background-color: #3c3f42;
    }

    QDoubleSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 16px;
        height: 12px;
        border: none;
        background-color: #3c3f42;
    }

    QDoubleSpinBox::up-arrow {
        width: 0;
        height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-bottom: 7px solid white;
    }

    QDoubleSpinBox::down-arrow {
        width: 0;
        height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 7px solid white;
    }
""")

            grid.addWidget(box, i, 1)
            self.spinboxes[label] = box

        control_layout.addLayout(grid)

        # Button
        compute_btn = QPushButton("Run Simulation")
        compute_btn.setStyleSheet("""
            QPushButton {
                background-color: #2f3236;
                color: white;
                border: 1px solid white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3a3d42;
            }
        """)
        compute_btn.clicked.connect(self.run_simulation)
        control_layout.addWidget(compute_btn)

        

        layout.addLayout(control_layout, 1)
        layout.addWidget(self.plot, 2)
        self.setLayout(layout)
        
        # Oscillation animation widget
        self.oscillation_widget = OscillationWidget(
            get_amplitude=lambda: self.spinboxes["Amplitude A (mm)"].value() / 1000,
            get_frequency=lambda: self.spinboxes["Frequency f (Hz)"].value()
        )
        self.oscillation_widget.setMinimumHeight(120)
        osc_container = QWidget()
        osc_container.setStyleSheet("""
            background-color: #24272b;
            border: 1px solid #4c4f52;
            border-radius: 8px;
            padding: 10px;
        """)

        osc_layout = QVBoxLayout()
        osc_container.setLayout(osc_layout)

        osc_label = QLabel("Bead Oscillation Preview")
        osc_label.setFont(QFont("Arial", 12, QFont.Bold))
        osc_label.setStyleSheet("color: white; padding-bottom: 6px;")
        osc_layout.addWidget(osc_label)

        self.oscillation_widget = OscillationWidget(
            get_amplitude=lambda: self.spinboxes["Amplitude A (mm)"].value() / 1000,
            get_frequency=lambda: self.spinboxes["Frequency f (Hz)"].value()
        )
        osc_layout.addWidget(self.oscillation_widget)

        control_layout.addWidget(osc_container)

    def run_simulation(self):
        # Extract user inputs
        A = self.spinboxes["Amplitude A (mm)"].value() / 1000  # mm → m
        f = self.spinboxes["Frequency f (Hz)"].value()
        m = self.spinboxes["Bead Mass m (g)"].value() / 1000    # g → kg
        mu = self.spinboxes["Viscosity µ (Pa·s)"].value()
        R0 = self.spinboxes["Initial Size R₀ (µm)"].value()
        R_target = self.spinboxes["Target Size Rₜ (µm)"].value()
        d = self.spinboxes["Tube Diameter d (mm)"].value() / 1000  # mm → m

         # Create model
        model = HomogenizerPhysics(A, f, m, mu, R0, R_target, d)
        self.plot.plot_decay(model)

        # Start oscillation
        self.oscillation_widget.start()

        # Plot
        self.plot.plot_decay(model)

from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ——— CLASS: Waveform Widget ——————————————————
class WaveformWidget(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(5, 1.5), dpi=100)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.setParent(parent)

        self.t = np.linspace(0, 2 * np.pi, 300)
        self.line, = self.ax.plot(self.t, np.sin(self.t), color='#90CAF9', lw=2)
        self.phase = 0

        self.ax.set_ylim(-1.2, 1.2)
        self.ax.axis('off')

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_wave)
        self.timer.start(30)

    def update_wave(self):
        self.phase += 0.2
        self.line.set_ydata(np.sin(self.t + self.phase))
        self.draw()

# ——————————————————————————————— CLASS: Welcome Screen ———————————————————————————————
class WelcomeScreen(QWidget):

    def update_background(self):
        self.gradient_phase += 0.002
        self.update()  # triggers paintEvent

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())

        # Animate color slowly
        color1 = QColor.fromHsvF((0.45 + 0.05 * np.sin(self.gradient_phase)) % 1, 0.3, 0.15)
        color2 = QColor.fromHsvF((0.50 + 0.05 * np.cos(self.gradient_phase)) % 1, 0.4, 0.25)
        color3 = QColor.fromHsvF((0.55 + 0.05 * np.sin(self.gradient_phase + 1)) % 1, 0.2, 0.1)

        gradient.setColorAt(0.0, color1)
        gradient.setColorAt(0.5, color2)
        gradient.setColorAt(1.0, color3)

        painter.fillRect(self.rect(), gradient)

    def __init__(self):
        super().__init__()

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(30)

        # Create a central widget to overlay text on the background
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignCenter)

        # Background Gradient (Deep marine blue + bio green)
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 600)
        gradient.setColorAt(0.0, QColor(15, 30, 45))     # Deep navy
        gradient.setColorAt(0.5, QColor(40, 100, 80))    # Biotech green
        gradient.setColorAt(1.0, QColor(10, 30, 20))     # Dark base
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # Translucent background for text
        text_bg = QWidget()
        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignCenter)
        text_bg.setStyleSheet("""
        background-color: rgba(255, 255, 255, 30);
        border-radius: 12px;
        padding: 20px;
        """)

        # Title
        title = QLabel("PHYZTECH HOMOGENIZER LAB")  # Main title
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setStyleSheet("color: #E0F7FA;")  # Soft blue
        title.setAlignment(Qt.AlignCenter)

        # Catch phrase
        tagline = QLabel("Unboxing the Physics of Biotech — Visualize. Simulate. Understand.")
        tagline.setFont(QFont("Arial", 14))
        tagline.setStyleSheet("color: #CDECEC;")
        tagline.setAlignment(Qt.AlignCenter)

        # Nest elements
        text_layout.addWidget(title)
        text_layout.addWidget(tagline)
        self.gradient_phase = 0.0
        self.bg_timer = QTimer(self)
        self.bg_timer.timeout.connect(self.update_background)
        self.bg_timer.start(50)
        text_bg.setLayout(text_layout)
        content_layout.addWidget(text_bg)
        content_widget.setLayout(content_layout)

        # Final layout
        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)


# ———————————————————————————————— CLASS: Home Screen with Navbar ————————————————————————————————
class HomeScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Homogenizer Software")
        self.setGeometry(100, 100, 1000, 700)

        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Navigation panel
        self.navbar = QListWidget()
        self.navbar.setFixedWidth(200)
        self.navbar.setSpacing(10)
        self.navbar.setStyleSheet("font-size: 16px;")
        self.navbar.addItem(QListWidgetItem("Home"))
        self.navbar.addItem(QListWidgetItem("Simulation"))
        self.navbar.addItem(QListWidgetItem("Settings (Coming Soon)"))
        self.navbar.addItem(QListWidgetItem("Help/About"))

        # Stacked content
        self.stack = QStackedWidget()
        self.stack.addWidget(WelcomeScreen())
        self.simulation_screen = HomogenizerSimulationScreen()
        self.stack.addWidget(self.simulation_screen)
        self.stack.addWidget(QLabel("Settings and Help will be added soon"))
        self.stack.addWidget(QLabel("About section (coming soon)"))

        # Hook up navigation
        self.navbar.currentRowChanged.connect(self.stack.setCurrentIndex)

        # Add to layout
        main_layout.addWidget(self.navbar)
        main_layout.addWidget(self.stack)
        self.navbar.setCurrentRow(0)  # Show welcome screen first


# ————————————————————————————————— CLASS: Oscillation Animation —————————————————————————————————
# ————————————————————————————————— CLASS: Oscillation Animation (Improved) —————————————————————————————————
# ————————————————————————————— CLASS: Enhanced Oscillation Visualization —————————————————————————————
class OscillationWidget(QWidget):
    def __init__(self, get_amplitude, get_frequency):
        super().__init__()
        self.get_amplitude = get_amplitude
        self.get_frequency = get_frequency
        self.phase = 0
        self.running = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(30)

        self.setMinimumHeight(160)
        self.setStyleSheet("""
        background-color: #202328;
        border: 1px solid #3c3f42;
        border-radius: 10px;
        """)

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        center_y = h // 2
        radius = 18

        # Tube body
        tube_rect = QRectF(20, center_y - 30, w - 40, 60)
        painter.setBrush(QColor(50, 60, 70))
        painter.setPen(QPen(QColor(90, 110, 130), 2))
        painter.drawRoundedRect(tube_rect, 20, 20)

        # Oscillation
        A = self.get_amplitude() * 100  # m → px
        f = self.get_frequency()
        if self.running:
            self.phase += 0.1 * f
        else:
            self.phase = 0

        x = int(w // 2 + (A * np.sin(self.phase) if self.running else 0))

        # Shadow
        painter.setBrush(QColor(30, 30, 30, 60))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(x - radius + 3, center_y - radius + 6, radius * 2, radius * 2)

        # Bead (gradient)
        gradient = QRadialGradient(x - radius // 2, center_y - radius // 2, radius * 2)
        gradient.setColorAt(0.0, QColor(170, 220, 255))
        gradient.setColorAt(1.0, QColor(0, 100, 200))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(20, 20, 20), 1))
        painter.drawEllipse(x - radius, center_y - radius, radius * 2, radius * 2)

        # Tube shading overlay (transparent top gloss)
        painter.setBrush(QColor(255, 255, 255, 15))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(tube_rect.adjusted(0, 0, 0, -35), 20, 20)

# —————————————————————————————————————————— MAIN ———————————————————————————————————————————
def main():
    app = QApplication(sys.argv)
    gui = HomeScreen()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()