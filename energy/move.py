import os, shutil

root = 'E:\\Simulations-Dec2009\\'
dest = 'C:\\Documents and Settings\\nsoares\\My Documents\\Code\\django\\relator\\energy\\data\\'

meterfile = lambda filename: filename.endswith('Meter.csv')

for (dirpath, dirnames, filenames) in os.walk(root):
	for filename in filter(meterfile, filenames):
		shutil.copy(os.path.join(root, dirpath, filename), dest)
		print filename
