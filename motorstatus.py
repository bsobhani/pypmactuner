from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtCore import QTimer
from communication import AsynRecord, Axis
from base import Base

status_bit_names = """Motor activated
Negative limit
Positive limit
Ext. servo alg.
Amplifier enabled
Open loop mode
Move timer
Integration mode
Dwell in progress
Data block error
Desired velocity
Abort decel. in
Block request
Home search in
User phase
User servo
Y-addr commute
Commutation
Posn follow offset
Posn follow enbl.
Capture on error
Software capture
Sign/magnitude
Rapid max
CS-1 # bit 3
CS-1 # bit 2
CS-1 # bit 1
CS-1 # bit 0
CS Axis definition
CS Axis definition
CS Axis definition
CS Axis definition
Assigned to CS
(Reserved)
Foreground in
Desired pos. limit
Stopped on limit
Home complete
Motor phase
Phasing search
Trigger move
Integrated fatal
I2T amplifier fault
Backlash
Amplifier fault
Fatal following
Warning following
In-position true"""


status_bit_names = status_bit_names.split("\n")

class MotorStatusGrid(QWidget):
	def clearLayout(self):
		for i in reversed(range(self.layout().count())): 
			widgetToRemove = self.layout().itemAt(i).widget()
			self.layout().removeWidget(widgetToRemove)
			widgetToRemove.setParent(None)
	def updateStatusFromBits(self, bits):
		self.clearLayout()
		for i in range(3):
			for j in range(16):
				count = i*16 + j
				n = 47 - count
				bitVal = (2**n & bits) > 0
				self.layout().addWidget(QLabel(status_bit_names[count]), j, 2*i)
				self.layout().addWidget(QLabel(str(bitVal)), j, 2*i+1)

	def readMotor(self):
		try:
			bits = self.axis.get_status()
		except TimeoutError:
			self.parent().emit_timeout_error()
			return
		self.updateStatusFromBits(bits)
		
		
		
		
	def __init__(self, axis_num, parent=None):
		super().__init__(parent)
		
		#self.connection = AsynRecord("XF:21IDD-CT{MC:PRV}Asyn")
		#self.axis = Axis(axis_num)
		self.axis = self.parent().controller.getAxis(axis_num)
		self.setLayout(QGridLayout())

class AxisSelector(QWidget):
	def setTargetAxis(self, n):
		self.jump_to_motor.setText(str(n))
	def targetAxis(self):
		return int(self.jump_to_motor.text())
	def updateAxis(self):
		self.axis.set_axis_num(self.targetAxis())
	def setAxis(self, n):
		self.setTargetAxis(n)
		self.updateAxis()


	def incrPage(self, n):
		current_page = self.axis.axis_num
		next_page = current_page + n
		self.setAxis(next_page)

	def nextPage(self):
		self.incrPage(1)

	def prevPage(self):
		self.incrPage(-1)

	def makeControlRow(self):
		layout = QHBoxLayout()
		jump_to_motor = QLineEdit()
		jump_to_motor.returnPressed.connect(self.updateAxis)
		self.jump_to_motor = jump_to_motor
		layout.addWidget(jump_to_motor)
		next_button = QPushButton(">")
		prev_button = QPushButton("<")
		next_button.clicked.connect(self.nextPage)
		prev_button.clicked.connect(self.prevPage)
		layout.addWidget(prev_button)
		layout.addWidget(next_button)
		return layout

	def __init__(self, axis, parent=None):
		super().__init__(parent)
		self.axis = axis
		self.setLayout(self.makeControlRow())

class MotorStatus(QWidget, Base):

		
	def doShowPage(self):
		if not self.guiErrorBit:
			self.motorgrid.readMotor()
	def __init__(self, axis_num=1, parent=None):
		super().__init__(parent)
		self.setLayout(QVBoxLayout())
		self.motorgrid = MotorStatusGrid(axis_num, self)
		self.layout().addWidget(self.motorgrid)
		control_row = AxisSelector(self.motorgrid.axis, self)
		self.layout().addWidget(control_row)

		control_row.setAxis(axis_num)

		self.timer = QTimer(self)
		self.timer.timeout.connect(self.doShowPage)
		self.timer.setInterval(1500)
		self.timer.start()
		

		




if __name__ == "__main__":
	app = QApplication([])
	motorstatus = MotorStatus()
	#motorstatus.updateStatusFromBits(hexstring_to_int("E40044000001"))
	motorstatus.show()
	app.exec()
