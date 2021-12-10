from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, QMainWindow, QMenu, QAction, QMdiArea, QMdiSubWindow, QGroupBox
from PyQt5.QtCore import QTimer
import time
from communication import AsynRecord, PmacSocket, NullSocket
from base import Base
import load_config


app = QApplication([])

from set_config import replace_or_append

class ChangeConnection(QWidget):
	def getCurrentPV(self):
		return self.mdi.currentSubWindow().widget().connection.pv_name

	def getAllSubWindows(self):
		return [x for x in self.mdi.subWindowList() if issubclass(x.widget().__class__, Base)]
		
	def changeAsynPVForWindow(self, w):
		pv = self.newPV.text()
		#w.widget().connection = AsynRecord(pv)
		w.widget().connection.set_pv(pv)
		w.widget().guiErrorBit = False
		print("set error bit false")
		#self.mdi.parent().statusBar().showMessage("PV set to: "+pv)
		
	def changeAsynPVAll(self):
		self.mdi.parent().global_asyn_pv = self.newPV.text()
		subWindows = self.getAllSubWindows()
		for w in subWindows:
			self.changeAsynPVForWindow(w)

	def setHostAll_(self, conn):
		#host = self.newHost.text()
		#port = int(self.newPort.text())
		#self.main_window.global_connection = PmacSocket(host, port)
		self.main_window.global_connection = conn
		subWindows = self.getAllSubWindows()
		for w in subWindows:
			#w.controller.set_pmac_socket(host, port)
			w.widget().controller.set_connection(self.main_window.global_connection)

	def setHostAll(self):
		try:
			host = self.newHost.text()
			port = int(self.newPort.text())
			self.setHostAll_(PmacSocket(host, port))
		except:
			self.setHostAll_(NullSocket())
		self.saveHost()

	def saveHost(self):
		replace_or_append("default_host = ", '"' + self.newHost.text() +'"\n')
		replace_or_append("default_port = ", self.newPort.text() + "\n")

	def loadHost(self):
		try:
			load_config.reload()
			host = load_config.default_host
			port = load_config.default_port
			self.newHost.setText(host)
			self.newPort.setText(str(port))
		except:
			None


	
	def __init__(self, mdi, parent=None):
		super().__init__(parent)
		self.mdi = mdi
		self.main_window = mdi.parent()
		self.setLayout(QVBoxLayout())
		self.pvGroupBox = QGroupBox("Change PV")
		self.pvGroupBox.setLayout(QHBoxLayout())
		l1 = self.pvGroupBox.layout()
		self.newPV = QLineEdit()
		try:
			pv = self.getCurrentPV()
		except:
			pv = ""
		self.newPV.setText(pv)
		self.pvGroupBox.layout().addWidget(self.newPV)
		self.submit = QPushButton("submit pv")
		self.submit.clicked.connect(self.changeAsynPVAll)
		self.pvGroupBox.layout().addWidget(self.submit)
		
		self.pmacSocketGroupBox = QGroupBox("Set Pmac Socket")
		self.newHost = QLineEdit()
		self.newPort = QLineEdit()
		self.hostSubmit = QPushButton("submit host/port")
		self.hostSubmit.clicked.connect(self.setHostAll)
		l2 = QHBoxLayout()
		self.pmacSocketGroupBox.setLayout(l2)
		l2.addWidget(self.newHost)
		l2.addWidget(self.newPort)
		l2.addWidget(self.hostSubmit)
		self.loadHost()

		self.layout().addWidget(self.pvGroupBox)
		self.layout().addWidget(self.pmacSocketGroupBox)
		

class MainWindow(QMainWindow):
	def updateConnection(self, w):
		conn = self.global_connection
		w.controller.set_connection(conn)
	def addToMdi(self, widget):
		sw = QMdiSubWindow(self)
		sw.setWidget(widget)
		self.mdi.addSubWindow(sw)
		sw.show()
		
	def run_terminal(self):
		from terminal import Terminal
		self.term = Terminal()
		#self.term.connection.set_pv(self.global_asyn_pv)
		self.updateConnection(self.term)
		self.term.errorSignal.connect(self.statusBar().showMessage)
		self.addToMdi(self.term)
		
	def run_ivar(self):
		from ivariableeditor import IVariableEditor
		self.editor = IVariableEditor()
		#self.editor.connection.set_pv(self.global_asyn_pv)
		self.updateConnection(self.editor)
		self.addToMdi(self.editor)
		
	def run_motorstatus(self):
		from motorstatus import MotorStatus
		self.motorstatus = MotorStatus()
		#self.motorstatus.connection.set_pv(self.global_asyn_pv)
		self.updateConnection(self.motorstatus)
		self.addToMdi(self.motorstatus)

	def run_jogger(self):
		from jogger import Jogger
		self.jogger = Jogger()
		#self.jogger.connection.set_pv(self.global_asyn_pv)
		self.updateConnection(self.jogger)
		self.addToMdi(self.jogger)


	def run_change_connection(self):
		self.change_connection = ChangeConnection(self.mdi, self)
		#self.change_connection.show()
		self.addToMdi(self.change_connection)


	def run_tuner(self):
		from tuner import Tuner
		self.tuner = Tuner()
		#self.tuner.show()
		#self.tuner.connection.set_pv(self.global_asyn_pv)
		self.updateConnection(self.tuner)
		self.addToMdi(self.tuner)
	def run_prog_viewer(self):
		from progviewer import ProgViewer
		self.progviewer = ProgViewer()
		#self.progviewer.connection.set_pv(self.global_asyn_pv)
		self.updateConnection(self.progviewer)
		self.addToMdi(self.progviewer)

	def run_motor_physical(self):
		from motorphysical import MotorPhysicalSetup
		self.motorphysical = MotorPhysicalSetup()
		#self.motorphysical.connection.set_pv(self.global_asyn_pv)
		self.updateConnection(self.motorphysical)
		self.addToMdi(self.motorphysical)
		
		
	def __init__(self, parent=None):
		super().__init__(parent)
		self.statusBar().showMessage("Ready")
		toolsMenu = QMenu("Tools", self)
		terminalAction = QAction("Terminal", self)
		iVarAction = QAction("I-Variable Editor", self)
		motorStatusAction = QAction("Motor Status", self)
		joggerAction = QAction("Jogger", self)
		tunerAction = QAction("Tuner", self)
		progViewerAction = QAction("View Prog/PLC", self)
		motorPhysicalAction = QAction("Motor Physical", self)
		changeConnectionAction = QAction("Change connection", self)
		terminalAction.triggered.connect(self.run_terminal)
		iVarAction.triggered.connect(self.run_ivar)
		motorStatusAction.triggered.connect(self.run_motorstatus)
		joggerAction.triggered.connect(self.run_jogger)
		tunerAction.triggered.connect(self.run_tuner)
		progViewerAction.triggered.connect(self.run_prog_viewer)
		motorPhysicalAction.triggered.connect(self.run_motor_physical)
		changeConnectionAction.triggered.connect(self.run_change_connection)
		toolsMenu.addAction(terminalAction)
		toolsMenu.addAction(iVarAction)
		toolsMenu.addAction(motorStatusAction)
		toolsMenu.addAction(joggerAction)
		toolsMenu.addAction(tunerAction)
		toolsMenu.addAction(progViewerAction)
		toolsMenu.addAction(motorPhysicalAction)
		toolsMenu.addAction(changeConnectionAction)
		self.menuBar().addMenu(toolsMenu)
		#widget = Tuner()
		self.mdi = QMdiArea()
		self.setCentralWidget(self.mdi)
		#self.global_asyn_pv = "XF:21IDD-CT{MC:03}Asyn"
		self.global_asyn_pv = "XF:10IDC-CT{MC:7}Asyn"
		self.global_connection = NullSocket()

	

if __name__ == "__main__":
	main_window = MainWindow()
	main_window.show()

	app.exec()
