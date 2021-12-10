from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QApplication, QDialog
from communication import AsynRecord, Controller
from PyQt5.QtCore import pyqtSignal
from base import Base

class Terminal(QWidget, Base):
	def __init__(self, parent=None):
		super().__init__(parent)
		#self.connection = AsynRecord("XF:21IDD-CT{MC:PRV}Asyn")
		self.setLayout(QVBoxLayout())
		self.messageBox = QTextEdit()
		self.messageBox.setReadOnly(True)
		self.layout().addWidget(self.messageBox)
		self.input = QLineEdit()
		self.input.returnPressed.connect(self.submit)
		self.layout().addWidget(self.input)

	def submit(self):
		cmd = self.input.text()
		try:
			r = self.controller.connection.send_recv(cmd)
		except TimeoutError:
			self.emit_timeout_error()
			return
		self.messageBox.append(r)

if __name__ == "__main__":
	app = QApplication([])
	terminal = Terminal()
	#terminal.controller.set_pmac_socket("192.168.11.21", 1025)
	terminal.controller.set_pmac_socket(None, None)
	terminal.show()
	app.exec()

	
