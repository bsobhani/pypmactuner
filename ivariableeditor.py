from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDialog
from communication import Controller
#from main import TextUpdate
from functools import partial
import time
from base import Base

class IVariableEditorRows(QWidget):
	def clearLayout(self):
		for i in reversed(range(self.layout().count())): 
			widgetToRemove = self.layout().itemAt(i).widget()
			self.layout().removeWidget(widgetToRemove)
			widgetToRemove.setParent(None)

	def set_ivar(self, ivar, callback, ivar_monitor):
		val = callback()
		self.controller.set_ivar(ivar, val)
		try:
			val = self.controller.get_ivar(ivar)
		except TimeoutError:
			self.parent().emit_timeout_error()
			return
		ivar_monitor.setText(str(val))

	def addRow(self, ivar):
		try:
			val = self.controller.get_ivar(ivar)
		except TimeoutError:
			self.parent().emit_timeout_error()
			return
		ivar_setter = QLineEdit()
		layout = QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(QLabel(str(ivar)))
		#layout.addWidget(TextUpdate(partial(self.controller.get_ivar, ivar)))
		ivar_monitor = QLabel(val)
		layout.addWidget(ivar_monitor)
		layout.addWidget(ivar_setter)
		ivar_setter.returnPressed.connect(partial(self.set_ivar, ivar, ivar_setter.text, ivar_monitor))
		row = QWidget()
		row.setLayout(layout)
		self.layout().addWidget(row)

	def refreshPage(self):
		self.showPage(int(self.starting_ivar))

	def showPage(self, starting_ivar):
		self.starting_ivar = int(starting_ivar)
		self.clearLayout()
		for i in range(10):
			ivar = int(starting_ivar) + i
			self.addRow(ivar)

	def nextPage(self):
		self.showPage(self.starting_ivar + 10)

	def prevPage(self):
		self.showPage(self.starting_ivar - 10)
		
	def __init__(self, parent):
		super().__init__(parent)
		#self.controller = Controller()
		self.controller = self.parent().controller
		self.setLayout(QVBoxLayout())
		try:
			self.showPage(800)
		except:
			None
		

class IVariableEditor(QWidget, Base):
	def doShowPage(self):
		ivar_num = int(self.jump_to_ivar.text())
		self.ivar_rows.showPage(ivar_num)
	def makeControlRow(self):
		layout = QHBoxLayout()
		jump_to_ivar = QLineEdit()
		jump_to_ivar.returnPressed.connect(self.doShowPage)
		self.jump_to_ivar = jump_to_ivar
		layout.addWidget(jump_to_ivar)
		next_button = QPushButton(">")
		prev_button = QPushButton("<")
		next_button.clicked.connect(self.ivar_rows.nextPage)
		prev_button.clicked.connect(self.ivar_rows.prevPage)
		layout.addWidget(prev_button)
		layout.addWidget(next_button)
		return layout
		
	def __init__(self, parent=None):
		super().__init__(parent)
		self.ivar_rows = IVariableEditorRows(self)
		self.setLayout(QVBoxLayout())
		self.layout().addWidget(self.ivar_rows)
		control_row = self.makeControlRow()
		self.layout().addLayout(control_row)

if __name__ == "__main__":
	app = QApplication([])
	widget = IVariableEditor()
	widget.controller.set_pmac_socket("192.168.11.21", 1025)
	widget.show()
	app.exec()
