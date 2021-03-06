from epics import caget, caput, pv
import time
from threading import Lock

from dls_pmaclib.dls_pmacremote import PmacEthernetInterface

class NullSocket:
	def send_recv(self, cmd):
		return "null socket"
	def send(self, cmd):
		self.send_recv(cmd)

class PmacSocket:
	def __init__(self, host, port):
		pei = PmacEthernetInterface()
		pei.hostname = host
		pei.port = port
		pei.connect()
		self.pei = pei

	def send_recv_raw(self, cmd):
		#print(cmd)
		#return "asdf"
		#cmd = bytes(cmd, encoding="ascii")
		return self.pei._sendCommand(cmd)
	def send_recv(self, cmd):
		#b = [ord(c) for c in cmd]
		#print(max(b), min(b), len(cmd))
		time.sleep(.1)
		#if max(b)>255:
		#	print([(cmd[i], b[i]) for i in range(len(cmd))])
		return self.send_recv_raw(cmd).split("\r")[0]
	def send(self, cmd):
		self.send_recv(cmd)




class AsynRecord:
	mutex = Lock()
	def done_waiting(self, value, **kwargs):
		self.recv_value = value
		self.waiting_for_mine = False
	def set_pv(self, pv_name):
		self.pv_name = pv_name
		self.send_pv_name = pv_name + ".AOUT"
		self.send_pv = pv.PV(self.send_pv_name)
		self.recv_pv_name = pv_name + ".AINP"
		self.recv_pv = pv.PV(self.recv_pv_name, callback=self.done_waiting)
	def __init__(self, pv_name):
		self.waiting_for_mine = False
		self.set_pv(pv_name)
	def send(self, msg):
		#caput(self.send_pv, msg)
		#self.waiting_for_mine = True
		#self.send_pv.put(msg)
		#time.sleep(.1)
		self.send_recv(msg)

	def recv(self):
		#return caget(self.recv_pv)
		response = self.recv_pv.get()
		return response

	def wait_for_response(self, timeout):
		time_elapsed = 0
		time_start = time.time()
		while self.waiting_for_mine:
			time.sleep(.001)
			time_elapsed = time.time() - time_start
			if time_elapsed > timeout:
				AsynRecord.mutex.release()
				raise TimeoutError

	def send_recv(self, msg, timeout=10):
		AsynRecord.mutex.acquire()
		self.waiting_for_mine = True
		#self.send(msg)
		self.send_pv.put(msg)

		self.wait_for_response(timeout)
		
		#return self.recv()
		val = self.recv_value
		#val = caget(self.recv_pv_name)
		AsynRecord.mutex.release()
		return val

	def set_ifmt(self, ifmt):
		pv = self.pv_name + ".IFMT"
		caput(pv, ifmt)

	def get_ifmt(self):
		pv = self.pv_name + ".IFMT"
		return caget(pv)
		

def compute_cs_string(cs):
	try:
		cs = int(cs)
		cs_string = "&" + str(cs) + " "
	except:
		cs_string = ""
	return cs_string

class Controller:
	def set_connection(self, conn):
		self.connection = conn
	def set_pmac_socket(self, host, port):
		self.set_connection(PmacSocket(host, port))
		
	def set_asyn_record(self, pv):
		self.set_connection(AsynRecord(pv))
		
	def __init__(self):
		#self.connection = AsynRecord("XF:21IDD-CT{MC:PRV}Asyn")
		#self.connection = AsynRecord("XF:21IDD-CT{MC:03}Asyn")
		#self.connection = AsynRecord("asdf")
		#self.connection = AsynRecord("XF:10IDC-CT{MC:7}Asyn")
		#self.connection = AsynRecord("XF:11IDB-CT{MC:11}Asyn")
		#self.connection = AsynRecord("XF:10IDC-CT{MC:7}Asyn")
		#self.connection = connection
		pass
	
	def get_ivar(self, ivar):
		response = self.connection.send_recv("i"+str(ivar)+"\r")
		return response
	def set_ivar(self, ivar, val):
		self.connection.send("i"+str(ivar)+"="+str(val)+"\r")
	def set_position(self, axis_num, pos):
		self.connection.send("#"+str(axis_num)+"j="+str(pos)+"\r")
	def get_position(self, axis_num):
		response = self.connection.send_recv("#"+str(axis_num) +"p\r")
		try:
			val = float(response)
		except ValueError:
			val = 0
		return val

	def get_following_error(self, axis_num):
		try:
			val = float(self.connection.send_recv("#{}F\r".format(axis_num)))
		except:
			val = 0
		return 0

	def kill_motor(self, axis_num):
		return self.connection.send("#{}K\r".format(axis_num))

	def stop_motor(self, axis_num):
		return self.connection.send("#{}J/\r".format(axis_num))

	def get_status(self, axis_num):
		s = self.connection.send_recv("#{}?\r".format(axis_num))
		try:
			i = int(s, 16)
		except ValueError:
			i = 0
		return i
	def in_position(self, axis_num):
		status = self.get_status(axis_num)
		return status%2==1

	def list_cmd(self, prog, cs=None):
		return self.list_cmd_method2(prog, cs)

	def list_cmd_method1(self, prog, cs):
		cs_string = compute_cs_string(cs)
		cmd = "list {}".format(prog)
		cmd = cs_string + cmd
		asynrecord = self.connection
		orig_ifmt = asynrecord.get_ifmt()
		asynrecord.set_ifmt("Binary")
		try:
			r = asynrecord.send_recv(cmd+" "+cmd, timeout = 6)
		except TimeoutError:
			r = caget(asynrecord.pv_name+".BINP")
			AsynRecord.mutex.release()
		asynrecord.set_ifmt(orig_ifmt)
		r = [chr(c) for c in r]
		r = ["\n" if c=="\r" else c for c in r]
		r = r[:-2]
		r = "".join(r)
		r = r[r.find("\n"):]
		return r

	def list_cmd_method2(self, prog, cs=None):
		cs_string = compute_cs_string(cs)
		cmd = "list {prog},{word},1"
		cmd = cs_string + cmd
		index = 1
		words = []
		while True:
			cmd_i = cmd.format(prog=prog, word=index)
			word = self.connection.send_recv(cmd_i)
			error_code = "\aERR003"
			if word==error_code:
				break
			if len(words)==0 or words[-1]!=word:
				print(cmd_i, word)
				words.append(word)
			index+=1
		r = "\n".join(words)
		return r
	
	def getAxis(self, num):
		return Axis(num, self)
		

class Axis:
	def __init__(self, axis_num, controller=None):
		if controller is None:
			controller = Controller()
		self.controller = controller
		self.set_axis_num(axis_num)

	def set_axis_num(self, axis_num):
		self.axis_num = axis_num

	def set_position_r(self, pos_r):
		current_pos = self.get_position()
		new_pos = current_pos + pos_r
		self.set_position(new_pos)
	def get_position(self):
		return self.controller.get_position(self.axis_num)
	def set_position(self, pos):
		self.controller.set_position(self.axis_num, pos)
	def get_following_error(self):
		return self.controller.get_following_error(self.axis_num)
	def get_status(self):
		return self.controller.get_status(self.axis_num)
	def in_position(self):
		return self.controller.in_position(self.axis_num)
	def kill_motor(self):
		return self.controller.kill_motor(self.axis_num)
	def stop_motor(self):
		return self.controller.stop_motor(self.axis_num)


	def get_axis_ivar(self, ivar_last_two_digits):
		ivar = self.axis_num*100 + ivar_last_two_digits
		return self.controller.get_ivar(ivar)
	def set_axis_ivar(self, ivar_last_two_digits, val):
		ivar = self.axis_num*100 + ivar_last_two_digits
		self.controller.set_ivar(ivar, val)

	def get_kp(self):
		return self.get_axis_ivar(30)
	def set_kp(self, val):
		self.set_axis_ivar(30, val)
	def get_velocity(self):
		return self.get_axis_ivar(22)
	def set_velocity(self, val):
		self.set_axis_ivar(22, val)
		
	
