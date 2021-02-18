import json
import requests
import sys
from PyPDF2 import PdfFileReader, PdfFileWriter
import re
import os
import pdf_to_txt
import omeka_interfacer as O

def filterup(level,next_level):
	final=[]
	for l in level:
		skip=False
		for nl in next_level:
			if l in nl:
				skip=True
		
		if skip==False:
			final.append(l)
	final+=next_level
	return final

def cleanstrs(list):
	list=[re.sub('^ ','',i,re.S) for i in list]
	list=[re.sub(' $','',i,re.S) for i in list]
	return(list)

def get_ne(text):
	text=re.sub('\n+',' ',text)
	text=re.sub('\s+',' ',text)
	text=re.sub('-',' ',text)
	cap='[A-Z][a-z]+\s*'
	singles=re.findall('(?<=[a-z] )'+cap,text,re.S)
	doubles=re.findall('(?<=[a-z] )'+cap+cap,text,re.S)
	triples=re.findall('(?<=[a-z] )'+cap+cap+cap,text,re.S)
	quads=re.findall('(?<=[a-z] )'+cap+cap+cap+cap,text,re.S)
	
	singles=cleanstrs(singles)
	doubles=cleanstrs(doubles)
	triples=cleanstrs(triples)
	quads=cleanstrs(quads)
		
	doubles=filterup(singles,doubles)
	triples=filterup(doubles,triples)
	quads=filterup(triples,quads)
	p=list(set(quads))
	return(p)

pdfs=O.omeka_get('media',args_dict={'o:media_type':'application/pdf'},retrieve_all=True)
pdf_named_entities={}

for m in pdfs:
	
	id=m['o:id']
	parent_id=m['o:item']['o:id']
	print(id,parent_id)
	
	#first, try to get a transcription from omeka
	if 'bibo:transcriptOf' in m:
		transcription=' '.join([t['@value'] for t in m['bibo:transcriptOf']])
	#then, try to get it from the pdf's text field
	else:
		dl=m['o:original_url']
		response=requests.get(dl,allow_redirects=True)
		open('temp.pdf','wb').write(response.content)
		pdf=PdfFileReader('temp.pdf')
		print(dl)
		c=0
		
		numpages=pdf.numPages
		transcription=''
		while c<numpages:
			page=pdf.getPage(c)
			pt=page.extractText()
			transcription+= ' ' +pt
			c+=1
		#os.remove('temp.pdf')
		
		if re.fullmatch('\s*',transcription):
			print('no transcript')
			print('fetching transcript...')
			transcription=pdf_to_txt.main('temp.pdf')
		print('writing transcript to media item properties in omeka...')
		O.update_item([{'term':'bibo:transcriptOf','type':'literal','value':transcription}],id,endpoint='media')
			
	ne = get_ne(transcription)
	
	print(ne)
	for n in ne:
		if n not in pdf_named_entities:
			pdf_named_entities[n]=[parent_id]
		else:
			pdf_named_entities[n].append(parent_id)
	
	if os.path.exists('pdfs.json'):
		d=open('pdfs.json','r')
		t=d.read()
		d.close()
		j=json.loads(t)
		for k in pdf_named_entities:
			j[k]=pdf_named_entities[k]
d=open('pdfs.json','w')	
t=d.write(json.dumps(pdf_named_entities))
d.close()

resource_class_id=O.omeka_get('resource_classes',{'term':'bibo:Note'})[0]['o:id']
notes=O.omeka_get('items',args_dict={'resource_class_id':resource_class_id},retrieve_all=True)
notes_named_entities={}
for note in notes:
	id=note['o:id']
	if 'acm5air:note' not in note.keys():
		print("no text in note ", id)
	else:
		notes_text=''
		for nt in note['acm5air:note']:
			notes_text+=nt['@value']
		ne=get_ne(notes_text)
		
		for n in ne:
			if n not in notes_named_entities:
				notes_named_entities[n]=[id]
			else:
				notes_named_entities[n].append(id)

d=open('notes.json','w')
t=d.write(json.dumps(notes_named_entities))
d.close()

d=open('notes.json','r')
t=d.read()
d.close()
notes=json.loads(t)
d=open('pdfs.json','r')
t=d.read()
d.close()
pdfs=json.loads(t)
intersection = set(list(pdfs.keys())) & set(list(notes.keys()))





intersection_dictionary={k:list(set(pdfs[k]+notes[k])) for k in intersection}
d=open('intersections.json','w')
d.write(json.dumps(intersection_dictionary))
d.close()
