import os
d = os.path.expanduser("~/.pypmactuner")
config_file = d + "/config.py"

def reload():
	f = open(config_file)
	s = f.read()
	f.close()

	exec(s, globals())

#reload()
#print(default_host)
#print(default_port)

