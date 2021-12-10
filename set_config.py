import os

#os.system("mkdir -p ~/.pypmactuner")
d = os.path.expanduser("~/.pypmactuner")
if not os.path.exists(d):
	os.mkdir(d)

config_file = os.path.expanduser('~/.pypmactuner/config.py')


#host_line = "default_host = 192.168.11.21\n"
#port_line = "default_port = 1025\n"

def replace_or_append(prefix, ending):
	if os.path.exists(config_file):
		f = open(config_file, 'r+')
	else:
		f = open(config_file, 'w+')

	l = f.readlines()
	flag = False
	line = prefix + ending
	for i in range(len(l)):
		#print(l[i])
		if l[i].startswith(prefix):
			l[i] = line
			flag = True
	if not flag:
		l.append(line)
	
	f.seek(0)
	for line in l:
		f.write(line)

	f.close()
	
		
#replace_or_append("default_host = ", "'192.168.11.21'\n")
#replace_or_append("default_port = ", "1025\n")


