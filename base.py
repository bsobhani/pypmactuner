from PyQt5.QtCore import pyqtSignal
from communication import Controller
class Base:
	errorSignal = pyqtSignal(str)
	def emit_timeout_error(self):
		self.guiErrorBit = True
		pv = self.connection.pv_name
		self.errorSignal.emit("Timeout Error when reading " + pv)
	def __init__(self, **kwargs):
		self.guiErrorBit = False
		self.controller = Controller()
		self.connection = self.controller.connection
	
