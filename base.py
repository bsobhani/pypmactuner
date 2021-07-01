from PyQt5.QtCore import pyqtSignal
from communication import Controller
class Base:
	errorSignal = pyqtSignal(str)
	def send_recv(self, cmd):
		try:
			r = self.connection.send_recv(cmd)
		except TimeoutError:
			self.errorSignal.emit("Timeout error")
			r = ""
		return r
	def __init__(self, **kwargs):
		self.controller = Controller()
		self.connection = self.controller.connection
	
