from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel
from communication import Controller
from epics import caget


class ProgViewer(QWidget):
	def loadText(self):
		prog_name = self.prog_name_input.text()
		cs = self.cs_input.text()
		text = self.controller.list_cmd(prog_name, cs)
		self.textarea.setText(text)
	def make_control_row(self):
		layout = QHBoxLayout()
		label = QLabel('Type prog name (e.g. "PLC7" or "Forward"): ')
		prog_name_input = QLineEdit()
		label_cs = QLabel('CS (optional): ')
		cs_input = QLineEdit()
		self.cs_input = cs_input
		self.prog_name_input = prog_name_input
		view_button = QPushButton("View Prog/PLC")
		self.view_button = view_button
		layout.addWidget(label)
		layout.addWidget(prog_name_input)
		layout.addWidget(label_cs)
		layout.addWidget(cs_input)
		layout.addWidget(view_button)
		return layout
		
	def __init__(self, parent=None):
		super().__init__(parent)
		self.controller = Controller()
		self.setLayout(QVBoxLayout())
		self.layout().addLayout(self.make_control_row())
		self.textarea = QTextEdit()
		self.layout().addWidget(self.textarea)
		
		self.view_button.clicked.connect(self.loadText) 
		

if __name__ == "__main__":
	app = QApplication([])
	widget = ProgViewer()
	widget.show()
	app.exec()

