import os, shutil

origin = "E:\Simulations-Dec2009"
destination = "C:\\Documents and Settings\\nsoares\\My Documents\\Code\\django\\relator\\data\\html"

for (dirpath, dirnames, filenames) in os.walk(origin):
	for name in filter(lambda s: s.endswith('.html'), filenames):
		start = os.path.join(dirpath, name)
		end = os.path.join(destination, name)
		shutil.copyfile(start, end)
