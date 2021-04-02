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
j=json.loads(t)

out_fname=fname[:-5]

with open(out_fname+'_nodes.csv','w') as csvfile:
	w = csv.writer(csvfile,quotechar='\"',delimiter=',')
	w.writerow(['id','modularity_class','label','size'])
	for node in j['nodes']:
		id=node['id']
		m=node['group']
		label=node['label']
		size=node['size']
		w.writerow([id,m,label,size])
		

with open(out_fname+'_edges.csv','w') as csvfile:
	w = csv.writer(csvfile,quotechar='\"',delimiter=',')
	w.writerow(['source','target','weight'])
	for e in j['links']:
		s=e['source']
		t=e['target']
		weight=e['value']
		w.writerow([s,t,weight])
		