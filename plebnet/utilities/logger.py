def log(type,subtype,msg):
	print fill(type,10) + " : " + fill(subtype,10) + " : " + msg

def fill(str,l):
	while(len(str)<l):
		str = str + " "
	return str