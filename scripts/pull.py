import os, shutil

origin = "E:\Simulations-Dec2009"
destination = "C:\\Documents and Settings\\nsoares\\My Documents\\Code\\django\\relator\\data\\html"

def ftwayne(name):
	if not name.endswith('.html'): return False
	if not name.startswith('O16'): return False
	if name.find('FORT_WAYNE') < 0: return False
	return True

for (dirpath, dirnames, filenames) in os.walk(origin):
	for name in filter(ftwayne, filenames):
		print name
		continue
		print 'moving', name
		start = os.path.join(dirpath, name)
		end = os.path.join(destination, rename)
		shutil.copyfile(start, end)
