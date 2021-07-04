from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QDoubleSpinBox
from PyQt5.QtCore import QTimer
from communication import Axis
from base import Base
from motorstatus import AxisSelector

class Jogger(QWidget, Base):
	def getAxisPosition(self):
		if self.guiErrorBit:
			return 0
		try:
			r = self.axis.get_position()
		except TimeoutError:
			self.emit_timeout_error()
			r = 0
		return r
	def updatePosition(self):
		self.readback.setText(str(self.getAxisPosition()))
	def syncSetpoint(self):
		self.setpoint.setValue(self.getAxisPosition())
	def getSetpoint(self):
		return self.setpoint.value()
	def setSetpoint(self, val):
		self.setpoint.setValue(val)
	def actuate(self):
		self.axis.set_position(self.getSetpoint())
	def moveToPosition(self, val):
		self.setSetpoint(val)
		self.actuate()
		

	def moveLeft(self):
		incr = self.increment.value()
		self.moveToPosition(self.getSetpoint() - incr)
	def moveRight(self):
		incr = self.increment.value()
		self.moveToPosition(self.getSetpoint() + incr)
	def __init__(self, axis_num=1, parent=None):
		super().__init__(parent)
		#self.axis = Axis(axis_num)
		self.axis = self.controller.getAxis(axis_num)
		self.axis_selector = AxisSelector(self.axis)
		self.setLayout(QHBoxLayout())
		self.readback = QLabel(self)
		self.setpoint = QDoubleSpinBox(self)
		self.setpoint.setMaximum(1000000000)
		self.setpoint.setButtonSymbols(2)
		self.setpoint.setKeyboardTracking(False)
		self.move_left = QPushButton("<", self)
		self.move_right = QPushButton(">", self)
		self.stop_button = QPushButton("Stop",  self)
		self.kill_button = QPushButton("Kill",  self)
		self.move_left.clicked.connect(self.moveLeft)
		self.move_right.clicked.connect(self.moveRight)
		self.stop_button.clicked.connect(self.axis.stop_motor)
		self.kill_button.clicked.connect(self.axis.kill_motor)
		self.increment = QDoubleSpinBox(self)
		self.increment.setMaximum(1000000000)
		self.increment.setButtonSymbols(2)
		self.increment.setKeyboardTracking(False)
		self.setpoint.valueChanged.connect(self.axis.set_position)
		self.layout().addWidget(self.setpoint)
		self.layout().addWidget(self.readback)
		self.layout().addWidget(self.move_left)
		self.layout().addWidget(self.increment)
		self.layout().addWidget(self.move_right)
		self.layout().addWidget(self.stop_button)
		self.layout().addWidget(self.kill_button)
		self.layout().addWidget(self.axis_selector)
		self.timer = QTimer(self)
		self.timer.setInterval(1500)
		self.timer.timeout.connect(self.updatePosition)
		self.timer.start()
		self.syncSetpoint()
		
	
if __name__ == "__main__":
	app = QApplication([])
	jogger = Jogger(axis_num=8)
	jogger.show()
	app.exec()
