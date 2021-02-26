import json
import requests
import sys
from PyPDF2 import PdfFileReader, PdfFileWriter
import re
import os
import pdf_to_txt
import omeka_interfacer as O


items=O.omeka_get('items',retrieve_all=True)

nodes={}
edges={}
classes=[]
for item in items:
	label=item['o:title']
	size=1
	id=item['o:id']
	rclass=item['o:resource_class']['o:id']
	connectionlist=[]
	for k in item:
		if type(item[k])==list and len(item[k])>0:
			for p in item[k]:
				if type(p)==dict:
					if 'type' in p and p['type']=='resource':
						connectionlist.append(p['value_resource_id'])
	if id in nodes:
		nodes[id]['label']=label
		nodes[id]['group']=rclass
	else:
		nodes[id]={'label':label,'group':rclass,'size':1}
	
	#print(connectionlist)
	
	for c in connectionlist:
		if c not in nodes:
			nodes[c]={'size':1}
		else:
			nodes[c]['size']+=1
		source=min(id,c)
		target=max(id,c)
		
		if source not in edges:
			edges[source]={target:1}
		elif target not in edges[source]:
			edges[source][target]=1
		else:
			edges[source][target]+=1

#print(nodes)
#print(edges)

nodesout=[{'id':i,'group':nodes[i]['group'],'label':nodes[i]['label'],'size':nodes[i]['size']} for i in nodes]

edgesout=[]
for source in edges:

	for target in edges[source]:
		edgesout.append({'source':source,'target':target,'value':edges[source][target]})

map={'nodes':nodesout,'links':edgesout}
d=open('map.json','w')
d.write(json.dumps(map))
d.close()

			
	
	