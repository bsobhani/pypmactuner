from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, QMainWindow, QMenu, QAction, QMdiArea, QMdiSubWindow
from PyQt5.QtCore import QTimer
import time


app = QApplication([])


class MainWindow(QMainWindow):
	def addToMdi(self, widget):
		sw = QMdiSubWindow(self)
		sw.setWidget(widget)
		self.mdi.addSubWindow(sw)
		sw.show()
		
	def run_terminal(self):
		from terminal import Terminal
		self.term = Terminal()
		self.addToMdi(self.term)
		
	def run_ivar(self):
		from ivariableeditor import IVariableEditor
		self.editor = IVariableEditor()
		self.addToMdi(self.editor)
		
	def run_motorstatus(self):
		from motorstatus import MotorStatus
		self.motorstatus = MotorStatus()
		self.addToMdi(self.motorstatus)

	def run_jogger(self):
		from jogger import Jogger
		self.jogger = Jogger()
		self.addToMdi(self.jogger)

	def run_tuner(self):
		from tuner import Tuner
		self.tuner = Tuner()
		self.tuner.show()
	def __init__(self, parent=None):
		super().__init__(parent)
		self.statusBar().showMessage("asdf")
		toolsMenu = QMenu("Tools", self)
		terminalAction = QAction("Terminal", self)
		iVarAction = QAction("I-Variable Editor", self)
		motorStatusAction = QAction("Motor Status", self)
		joggerAction = QAction("Jogger", self)
		tunerAction = QAction("Tuner", self)
		terminalAction.triggered.connect(self.run_terminal)
		iVarAction.triggered.connect(self.run_ivar)
		motorStatusAction.triggered.connect(self.run_motorstatus)
		joggerAction.triggered.connect(self.run_jogger)
		tunerAction.triggered.connect(self.run_tuner)
		toolsMenu.addAction(terminalAction)
		toolsMenu.addAction(iVarAction)
		toolsMenu.addAction(motorStatusAction)
		toolsMenu.addAction(joggerAction)
		toolsMenu.addAction(tunerAction)
		self.menuBar().addMenu(toolsMenu)
		#widget = Tuner()
		self.mdi = QMdiArea()
		self.setCentralWidget(self.mdi)

	

if __name__ == "__main__":
	main_window = MainWindow()
	main_window.show()

	app.exec()
