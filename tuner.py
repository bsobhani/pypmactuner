from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, QMainWindow
from PyQt5.QtCore import pyqtSignal, QThread, QObject
from communication import Controller, Axis
import pyqtgraph as pg
import numpy as np
from functools import partial
from PyQt5.QtCore import QTimer
import time
import threading
from base import Base
from motorstatus import AxisSelector

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
	def addSingleValToSinglePlot(self, channel, val):
		array = val
		colors = "wy"
		while len(self.plots)-1<channel:
			color = colors[channel % len(colors)]
			p = self.plot(pen=pg.mkPen(color))
			self.plots.append(p)
		while len(self.plot_data)-1<channel:
			self.plot_data.append(np.array([]))
		self.plot_data[channel] = np.append(self.plot_data[channel], array)
		self.plots[channel].setData(self.plot_data[channel])

	def addValsToPlots(self, vals):
		for i in range(len(vals)):
			self.addSingleValToSinglePlot(i, vals[i])
		
	def __init__(self):
		super().__init__()
		self.clear_data()
	def clear_data(self):
		self.index = 0
		self.plots = []
		self.plot_data = []
	def plotVal(self, val):
		#self.plot([self.index], [val], pen=None, symbol='o')
		#self.index += 1
		self.plotArray([val], color)
	def plotArray(self, array, index=None, color="w"):
		if index is None:
			index = self.index
		length = len(array)
		end = index + length
		indices = list(range(index, end))
		#self.plot(indices, array, pen=None, symbol='o')
		self.plot(indices, array, pen=pg.mkPen(color))
		self.index = end
	def plotPoint(self, point):
		index = point[0]
		for i in range(1, len(point)):
			if i%2==0:
				color = "w"
			else:
				color = "y"
			self.plotArray([point[i]], index, color)

class Sampler(QObject):
	pointSignal = pyqtSignal(list)
	def take_sample(self, channel_num):
		sample_callback = self.sample_callbacks[channel_num]
		sample = sample_callback()
		self.data[channel_num] = np.append(self.data[channel_num], sample)
	def get_last_point(self):
		n = len(self.data[0]) - 1
		L = [n]
		for i in range(len(self.data)):
			L.append(self.data[i][n])
		return L
	def take_all_samples(self):
		for i in range(len(self.sample_callbacks)):
			self.take_sample(i)
		self.pointSignal.emit(self.get_last_point())
	def __init__(self, sample_callbacks, sampling_rate):
		#self.sample_callback = sample_callback
		super().__init__()
		self.sample_callbacks = sample_callbacks
		self.clear()
		self.sampling_rate = sampling_rate
		self.running = False
	def clear(self):
		self.data = [np.array([]) for x in self.sample_callbacks]

	def sample_chain(self):
		self.take_all_samples()
		if self.running:
			threading.Timer(self.sampling_rate, self.sample_chain).start()
		else:
			print("terminating sampling")
			self.done = True
	
	def start(self):
		if self.running:
			return
		self.running = True
		self.done = False
		self.clear()
		self.sample_chain()
	def stop(self):
		print("Stopping sampling")
		self.running = False
		while not self.done:
			time.sleep(.001)
		
	


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

def wait_until_in_position(axis):
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

class DoStepThread(QThread):
	finished2 = pyqtSignal()
	def setStepSize(self, step_size):
		self.step_size = step_size
	def __init__(self, sampler, axis, parent=None):
		super().__init__(parent)
		self.sampler = sampler
		self.axis = axis

	def run(self):
		#self.scope.clear()
		print("begin do step")
		axis = self.axis
		start_position = axis.get_position()
		axis.set_position_r(self.step_size)
		wait_until_in_position(axis)
		axis.set_position(start_position)
		wait_until_in_position(axis)
		#self.sampler.stop()
		#actual_position = self.sampler.data[0]
		#index = self.scope.index
		#self.scope.plotArray(actual_position, index)
		#following_error = self.sampler.data[1]
		#commanded_position = actual_position + following_error
		#self.scope.plotArray(commanded_position, index, color="y")
		#self.error_area.setText("Error sum sq.: " + str(sum(following_error*following_error)))
		print("end do step")
		self.finished2.emit()
		
	

class Tuner(QWidget, Base):
	def addIvarRow(self, ivar, title):
		line = create_ivar_row(self.axis, ivar, title)
		self.settings_pane.addLayout(line)

	def __init__(self, parent=None):
		super().__init__(parent)
		self.axis = axis
		self.axis_selector = AxisSelector(self.axis)
		self.lr_layout = QHBoxLayout()
		self.settings_pane = QVBoxLayout()
		self.setLayout(self.lr_layout)
		self.scope = Scope()
		self.lr_layout.addWidget(self.scope)
		self.lr_layout.addLayout(self.settings_pane)
		self.error_area = QLabel("Error area: ")
		self.settings_pane.addWidget(self.error_area)
		velocity_input = QLineEdit()
		step_size_input = QLineEdit()
		kp_input = QLineEdit()
		#settings_button = QPushButton()
		#settings_button.clicked.connect(self.submit_settings)
		step_button = QPushButton("Do step")
		step_button.clicked.connect(self.do_step)
		self.addIvarRow(11, "following error (fatal)")
		self.addIvarRow(12, "following error (warning)")
		self.addIvarRow(22, "velocity")
		self.addIvarRow(30, "kp")
		self.addIvarRow(31, "kd")
		self.addIvarRow(32, "kff")
		self.addIvarRow(33, "ki")
		#self.layout().addWidget(settings_button)
		line = QHBoxLayout()
		line.addWidget(QLabel("step size"))
		line.addWidget(step_size_input)
		self.settings_pane.addLayout(line)
		self.settings_pane.addWidget(step_button)
		self.settings_pane.addWidget(self.axis_selector)

		self.kp_input = kp_input
		self.velocity_input = velocity_input
		self.step_size_input = step_size_input

		self.sampler = Sampler([self.axis.get_position, self.axis.get_following_error], .1)
		self.do_step_thread = DoStepThread(self.sampler, self.axis)
		self.do_step_thread.finished2.connect(self.step_done)
		#self.sampler.pointSignal.connect(print)
		self.sampler.pointSignal.connect(self.processAndPlotPoint)

	def processAndPlotPoint(self, point):
		index = point[0]
		actual_position = point[1]
		following_error = point[2]
		commanded_position = actual_position + following_error
		#self.scope.plotArray([actual_position], index)
		self.scope.addValsToPlots([actual_position, commanded_position])
		#self.scope.plotArray([commanded_position], index, "y")
		

	def submit_settings(self):
		kp_val = float(self.kp_input.text())
		velocity_val = float(self.velocity_input.text())
		axis.set_kp(kp_val)
		axis.set_velocity(velocity_val)
		print("Done submitting settings")

	"""
	def do_step(self):
		self.scope.clear()
		print("begin do step")
		step_size_val = float(self.step_size_input.text())
		start_position = axis.get_position()
		self.sampler.start()
		axis.set_position_r(step_size_val)
		wait_until_in_position()
		axis.set_position(start_position)
		wait_until_in_position()
		self.sampler.stop()
		actual_position = self.sampler.data[0]
		index = self.scope.index
		self.scope.plotArray(actual_position, index)
		following_error = self.sampler.data[1]
		commanded_position = actual_position + following_error
		self.scope.plotArray(commanded_position, index, color="y")
		self.error_area.setText("Error sum sq.: " + str(sum(following_error*following_error)))
		print("end do step")
	"""
	def do_step(self):
		self.scope.clear()
		self.scope.clear_data()
		step_size_val = float(self.step_size_input.text())
		self.do_step_thread.setStepSize(step_size_val)
		self.sampler.start()
		self.do_step_thread.start()
		#self.sampler.stop()
	def step_done(self):
		self.sampler.stop()
		following_error = self.sampler.data[1]
		self.error_area.setText("Error sum sq.: " + str(sum(following_error*following_error)))

if __name__ == "__main__":
	app = QApplication([])
	tuner = Tuner()
	tuner.axis.controller.set_pmac_socket("192.168.11.21", 1025)
	tuner.show()
	app.exec()
