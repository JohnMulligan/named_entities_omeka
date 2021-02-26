import re
import csv
import json
import sys

fname=sys.argv[1]
print(fname)

if not fname.endswith('.json'):
	print('needs .json input file')
	exit()

d=open(fname,'r')
t=d.read()
d.close()
keywords=json.loads(t)

out_fname=fname[:-5]

with open(out_fname+'.csv','w') as csvfile:
	w = csv.writer(csvfile,quotechar='\"',delimiter=',')
	w.writerow(['keyword','links','count'])
	for kw in keywords:
		linklist=[str(k) for k in keywords[kw]]
		links=','.join(linklist)
		row=[kw,links,str(len(linklist))]
		w.writerow(row)


	