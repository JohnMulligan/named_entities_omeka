import json
import re

for f in ['pdfs.json','notes.json']:
	d=open(f)
	t=d.read()
	j=json.loads(t)
	d.close()
	
	outf=re.sub('\.json','.txt',f)
	
	print(outf)
	d=open(outf,'w')
	
	lines=[]
	for l in list(j.keys()):
		count=len(j[l])
		label=l
		lines.append(label + ',' + str(count))
		
	d.write('\n'.join(lines))
	d.close()
