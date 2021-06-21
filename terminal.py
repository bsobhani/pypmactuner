from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QApplication, QDialog
from communication import AsynRecord

class Terminal(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.connection = AsynRecord("XF:21IDD-CT{MC:PRV}Asyn")
		self.setLayout(QVBoxLayout())
		self.messageBox = QTextEdit()
		self.messageBox.setReadOnly(True)
		self.layout().addWidget(self.messageBox)
		self.input = QLineEdit()
		self.input.returnPressed.connect(self.send_recv)
		self.layout().addWidget(self.input)

	def send_recv(self):
		cmd = self.input.text()
		self.connection.send(cmd)
		self.messageBox.append(self.connection.recv())

if __name__ == "__main__":
	app = QApplication([])
	terminal = Terminal()
	terminal.show()
	app.exec()

	
