import telnetlib
import time
import commands
host = "hack.bckdr.in"
port = 8010
tn = telnetlib.Telnet(host,port)
print tn.read_until('can')
i = 0
while True:
	i+= 1
	print i
	data = tn.read_until('none',1)
	print data
	data = data.replace('\x20\x20',' ')
	data = data.replace("\xe2\x96\x88\xe2\x96\x88","X")
	data = data.split("\n")
	result = ''
	for a in data:
		if 'X' in a:
			a=a[1:-1]
			result += a
			result += '\n'
	filename = 'qr'
	f = open(filename,'w')
	f.write(result)
	f.close()
	kq = commands.getoutput('python ./sqrd.py '+filename)
	print kq
	tn.write(kq + "\n")
#Congratulations. Flag is ca98c04be2505d686c5720675db2fe52111a52262490d0b12c158de0c96cdcd9