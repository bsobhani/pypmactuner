from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QApplication, QDialog, QPushButton
from communication import AsynRecord, Controller
from PyQt5.QtCore import pyqtSignal
from base import Base

class CodeRunner(QWidget, Base):
	def __init__(self, parent=None):
		super().__init__(parent)
		#self.connection = AsynRecord("XF:21IDD-CT{MC:PRV}Asyn")
		self.setLayout(QVBoxLayout())
		#self.messageBox = QTextEdit()
		#self.messageBox.setReadOnly(True)
		#self.layout().addWidget(self.messageBox)
		self.input = QTextEdit()
		#self.input.returnPressed.connect(self.submit)
		self.submitButton = QPushButton("Run code")
		self.submitButton.clicked.connect(self.submit)
		self.layout().addWidget(self.input)
		self.layout().addWidget(self.submitButton)

	def submit(self):
		cmd = self.input.toPlainText()
		#print(cmd)
		#print(cmd.split('\n'))
		cmd = cmd.split('\n')
		#print(cmd)
		try:
			for line in cmd:
				r = self.controller.connection.send_recv(line+"\r")
		except TimeoutError:
			self.emit_timeout_error()
			return
		#self.messageBox.append(r)

if __name__ == "__main__":
	app = QApplication([])
	terminal = CodeRunner()
	terminal.controller.set_pmac_socket("192.168.11.21", 1025)
	#terminal.controller.set_pmac_socket(None, None)
	terminal.show()
	app.exec()

	
