from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from functools import partial
from communication import Axis
from tuner import create_ivar_row, TextUpdate
from motorstatus import AxisSelector
from base import Base

def max_current_cb(axis):
	i01 = float(axis.get_axis_ivar(1))
	i69 = float(axis.get_axis_ivar(69))
	i77 = float(axis.get_axis_ivar(77))
	return "Max current: sqrt(Ixx01*Ixx69^2 + Ixx77^2) = " + str((i01*i69**2 + i77**2)**.5)


def gear_ratio_cb(axis):
	i07 = float(axis.get_axis_ivar(7))
	i08 = float(axis.get_axis_ivar(8))
	return "Gear ratio: Ixx07/Ixx08 = " + str(i07/i08)

class MotorPhysicalSetup(QWidget, Base):
	def addIvarRow(self, ivar, title):
		row = create_ivar_row(self.axis, ivar, title+" (Ixx{:02d}): ".format(ivar))
		self.layout().addLayout(row)
	def __init__(self, axis_num=1, parent=None):
		super().__init__()
		#self.axis = Axis(axis_num)
		self.axis = self.controller.getAxis(axis_num)
		self.setLayout(QVBoxLayout())
		self.addIvarRow(1, "Commutation enable")
		self.addIvarRow(70, "Num. commutation cycles")
		self.addIvarRow(69, "Command output limit")
		self.addIvarRow(77, "Magnetization current")
		self.layout().addWidget(TextUpdate(partial(max_current_cb, self.axis)))
		self.addIvarRow(7, "Master scale factor")
		self.addIvarRow(8, "Position scale factor")
		self.layout().addWidget(TextUpdate(partial(gear_ratio_cb, self.axis)))

		self.axis_selector = AxisSelector(self.axis)
		self.layout().addWidget(self.axis_selector)
		

if __name__ == "__main__":
	app = QApplication([])
	widget = MotorPhysicalSetup()
	widget.show()
	app.exec()
