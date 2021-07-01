from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, QMainWindow
from communication import Controller, Axis
import pyqtgraph as pg
import numpy as np
from functools import partial
from PyQt5.QtCore import QTimer
import time
import threading

class TextUpdate(QLabel):
	def __init__(self, func, parent=None):
		super().__init__(parent)
		self.func = func
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.setInterval(1500)
		self.timer.start()
	def update(self):
		self.setText(str(self.func()))
	

class Scope(pg.PlotWidget):
	def __init__(self):
		super().__init__()
		self.index = 0
	def plotVal(self, val):
		#self.plot([self.index], [val], pen=None, symbol='o')
		#self.index += 1
		self.plotArray([val])
	def plotArray(self, array):
		length = len(array)
		end = self.index + length
		indices = list(range(self.index, end))
		self.plot(indices, array, pen=None, symbol='o')
		self.index = end

class Sampler:
	def take_sample(self):
		sample = self.sample_callback()
		self.data = np.append(self.data, sample)
	def __init__(self, sample_callback, sampling_rate):
		self.sample_callback = sample_callback
		self.sampling_rate = sampling_rate
		self.data = np.array([])
		self.running = False
	def clear(self):
		self.data = np.array([])

	def sample_chain(self):
		self.take_sample()
		if self.running:
			threading.Timer(self.sampling_rate/1000, self.sample_chain).start()
	
	def start(self):
		if self.running:
			return
		self.running = True
		self.clear()
		self.sample_chain()
	def stop(self):
		self.running = False
		
	


def plot_for_milliseconds(scope, t):
	dwell_start = time.time()
	while time.time()-dwell_start<t/1000:
		y = axis.get_position()
		scope.plotVal(y)
		time.sleep(.001)

def plot_until_in_position(scope):
	time.sleep(.1)
	while not axis.in_position():
		y = axis.get_position()
		scope.plotVal(y)

def wait_until_in_position():
	time.sleep(.1)
	while not axis.in_position():
		time.sleep(.1)




#axis = Axis(7)
axis = Axis(3)

def send_le_to_ivar(axis, ivar, le):
	txt = le.text()
	axis.set_axis_ivar(ivar, txt)

def create_ivar_row(axis, ivar, title):
	ivar_input = QLineEdit()
	line = QHBoxLayout()
	line.addWidget(QLabel(title))
	line.addWidget(TextUpdate(partial(axis.get_axis_ivar, ivar)))
	line.addWidget(ivar_input)
	ivar_input.returnPressed.connect(partial(send_le_to_ivar, axis, ivar, ivar_input))
	return line

class Tuner(QWidget):
	def addIvarRow(self, ivar, title):
		line = create_ivar_row(self.axis, ivar, title)
		self.layout().addLayout(line)

	def __init__(self, parent=None):
		super().__init__(parent)
		self.axis = axis
		self.setLayout(QVBoxLayout())
		self.scope = Scope()
		self.layout().addWidget(self.scope)
		velocity_input = QLineEdit()
		step_size_input = QLineEdit()
		kp_input = QLineEdit()
		settings_button = QPushButton()
		settings_button.clicked.connect(self.submit_settings)
		step_button = QPushButton()
		step_button.clicked.connect(self.do_step)
		self.addIvarRow(11, "following error (fatal)")
		self.addIvarRow(12, "following error (warning)")
		self.addIvarRow(22, "velocity")
		self.addIvarRow(30, "kp")
		self.addIvarRow(31, "kd")
		self.addIvarRow(32, "kff")
		self.addIvarRow(33, "ki")
		self.layout().addWidget(settings_button)
		line = QHBoxLayout()
		line.addWidget(QLabel("step size"))
		line.addWidget(step_size_input)
		self.layout().addLayout(line)
		self.layout().addWidget(step_button)

		self.kp_input = kp_input
		self.velocity_input = velocity_input
		self.step_size_input = step_size_input

		self.sampler = Sampler(self.axis.get_position, .1)

	def submit_settings(self):
		kp_val = float(self.kp_input.text())
		velocity_val = float(self.velocity_input.text())
		axis.set_kp(kp_val)
		axis.set_velocity(velocity_val)
		print("Done submitting settings")

	def do_step(self):
		self.scope.clear()
		print("begin do step")
		step_size_val = float(self.step_size_input.text())
		start_position = axis.get_position()
		self.sampler.start()
		axis.set_position_r(step_size_val)
		#plot_until_in_position(self.scope)
		wait_until_in_position()
		#plot_for_milliseconds(self.scope, 5000)
		axis.set_position(start_position)
		wait_until_in_position()
		#plot_until_in_position(self.scope)
		self.sampler.stop()
		self.scope.plotArray(self.sampler.data)
		print("end do step")


if __name__ == "__main__":
	app = QApplication([])
	tuner = Tuner()
	tuner.show()
	app.exec()
