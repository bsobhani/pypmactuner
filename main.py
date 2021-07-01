from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, QMainWindow, QMenu, QAction, QMdiArea, QMdiSubWindow
from PyQt5.QtCore import QTimer
import time
from communication import AsynRecord


app = QApplication([])

class ChangeConnection(QWidget):
	def getCurrentPV(self):
		return self.mdi.currentSubWindow().widget().connection.pv_name
	def changeAsynPVForWindow(self, w):
		pv = self.newPV.text()
		w.widget().connection = AsynRecord(pv)
		#self.mdi.parent().statusBar().showMessage("PV set to: "+pv)
		
	def changeAsynPVAll(self):
		subWindows = self.mdi.subWindowList()
		for w in subWindows:
			self.changeAsynPVForWindow(w)
	
	def __init__(self, mdi, parent=None):
		super().__init__(parent)
		self.mdi = mdi
		self.setLayout(QHBoxLayout())
		self.newPV = QLineEdit()
		try:
			pv = self.getCurrentPV()
		except:
			pv = ""
		self.newPV.setText(pv)
		self.layout().addWidget(self.newPV)
		self.submit = QPushButton("submit")
		self.submit.clicked.connect(self.changeAsynPVAll)
		self.layout().addWidget(self.submit)

class MainWindow(QMainWindow):
	def addToMdi(self, widget):
		sw = QMdiSubWindow(self)
		sw.setWidget(widget)
		self.mdi.addSubWindow(sw)
		sw.show()
		
	def run_terminal(self):
		from terminal import Terminal
		self.term = Terminal()
		self.term.errorSignal.connect(self.statusBar().showMessage)
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


	def run_change_connection(self):
		self.change_connection = ChangeConnection(self.mdi, self)
		#self.change_connection.show()
		self.addToMdi(self.change_connection)


	def run_tuner(self):
		from tuner import Tuner
		self.tuner = Tuner()
		self.tuner.show()
	def __init__(self, parent=None):
		super().__init__(parent)
		self.statusBar().showMessage("Ready")
		toolsMenu = QMenu("Tools", self)
		terminalAction = QAction("Terminal", self)
		iVarAction = QAction("I-Variable Editor", self)
		motorStatusAction = QAction("Motor Status", self)
		joggerAction = QAction("Jogger", self)
		tunerAction = QAction("Tuner", self)
		changeConnectionAction = QAction("Change connection", self)
		terminalAction.triggered.connect(self.run_terminal)
		iVarAction.triggered.connect(self.run_ivar)
		motorStatusAction.triggered.connect(self.run_motorstatus)
		joggerAction.triggered.connect(self.run_jogger)
		tunerAction.triggered.connect(self.run_tuner)
		changeConnectionAction.triggered.connect(self.run_change_connection)
		toolsMenu.addAction(terminalAction)
		toolsMenu.addAction(iVarAction)
		toolsMenu.addAction(motorStatusAction)
		toolsMenu.addAction(joggerAction)
		toolsMenu.addAction(tunerAction)
		toolsMenu.addAction(changeConnectionAction)
		self.menuBar().addMenu(toolsMenu)
		#widget = Tuner()
		self.mdi = QMdiArea()
		self.setCentralWidget(self.mdi)

	

if __name__ == "__main__":
	main_window = MainWindow()
	main_window.show()

	app.exec()
