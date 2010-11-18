import os, shutil

origin = "E:\Simulations-Dec2009"
destination = "C:\\Documents and Settings\\nsoares\\My Documents\\Code\\django\\relator\\data\\html"

for (dirpath, dirnames, filenames) in os.walk(destination):
	for name in filter(lambda s: s.find('OHARE') != -1, filenames):
		os.remove(os.path.join(destination, name))
		print 'got one'
for (dirpath, dirnames, filenames) in os.walk(destination):
	for name in filter(lambda s: s.find('LA_GUARDIA') != -1, filenames):
		os.remove(os.path.join(destination, name))
		print 'got one'
