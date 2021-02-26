import json
import requests
import sys
from PyPDF2 import PdfFileReader, PdfFileWriter
import re
import os
import pdf_to_txt
import omeka_interfacer as O
import string


def get_ne(txt):
	txt=re.sub('\n-','',txt)
	txt=re.sub('-\n','',txt)
	txt=re.sub('\n+',' ',txt)
	txt=re.sub('[0-9]+','',txt)
	
	txt=re.sub('™','\'',txt)
	txt=re.sub('Š',' (',txt)
	
	txt=re.sub('-',' ',txt)
	txt=re.sub('\s+',' ',txt)
	#print(txt)
	joiners=re.compile("(de|da|do|das|dos|a|o|de la|del|de las|de los|la|el|du|de l\'|des|le|au|of|of the|and Sons|and Company)")
	doublejoiners=re.compile("(de la|de las|de los|de l\'|of the|and Sons|and Company)")
	proper=re.compile('[A-ZÀÁÃÂÉÊÍÓÔÕÚÜÇ][a-zàáãâéêíóôõúüçéàèùâêîôûáéíóúüñ\']+')
	d=open('known_baddies.txt','r')
	t=d.read()
	d.close()
	l=t.split('\n')
	known_baddies=[i.strip() for i in l]
	tokenized=[i for i in txt.split(' ')]
	ocrproblems=re.compile('ﬂ$')
	tokenized=[re.sub(ocrproblems,'',i) for i in tokenized]
	tokenized=[i for i in tokenized if len(i)>0]
	#print(txt)
	#print(tokenized)
	breaker_punctuation='[!"#$%&\()*+,./:;<=>?@[\\]^_`{|}~¿¡“”]'
	eos_punctuation=['?','.','!']
	titles_and_initials='Dr\.|Mrs\.|Ms\.|Mr\.|Fra\.|Sr\.|Srta\.|Sra\.|PhD\.|Ph\.D\.|[A-Z]\.|Hon\.'
	allmatches=[]
	runningmatch=[]
	c=0
	while c<len(tokenized):
		breaker=False
		try:
			t=tokenized[c]
		except:
			break
		
		#print(t)
		
		if re.match(proper,t) and t not in known_baddies:
			clean_t=re.sub(breaker_punctuation,'',t)
			if clean_t!=t and not re.fullmatch(titles_and_initials,t):
				if re.match('.*'+breaker_punctuation+'$',t) and len(runningmatch)!=0:
					runningmatch.append(clean_t)
					breaker=True
				elif re.match(breaker_punctuation+'+',t) and len(runningmatch==0):
					runningmatch.append(clean_t)
				else:
					runningmatch.append(clean_t)
					breaker=True
			else:
				runningmatch.append(t)
		elif re.fullmatch(doublejoiners,' '.join([tokenized[c],tokenized[(c+1)%(len(tokenized)-1)]])) and len(runningmatch)>0:
			t=' '.join([tokenized[c],tokenized[c+1]])
			runningmatch.append(t)
			c+=1				
		elif re.fullmatch(joiners,t) and len(runningmatch)>0:
			runningmatch.append(t)
		else:
			breaker=True
		
		if t[-1] in eos_punctuation:
			breaker=True
			c+=1
		
		c+=1
		
		if breaker==True and len(runningmatch)>0:
			while re.fullmatch(joiners,runningmatch[-1]):
				del(runningmatch[-1])
			if len(runningmatch)>0:
				strmatch=' '.join(runningmatch)
				if strmatch.endswith('\'s') or strmatch.endswith('’s'):
					strmatch=strmatch[:-2]
				allmatches.append(strmatch)
			runningmatch=[]
	PN=list(set(allmatches))
	#print(PN)
	maximal=[]
	for n in PN:
		skip=False
		for o in PN:
			if n in o and n!=o:
				skip=True
		if skip==False:
			maximal.append(n)
	return maximal




def preprocess_pdf(fname='temp.pdf'):
	from pikepdf import Pdf
	tmp_output_file_path = fname+'.tmp'
	final_input_file_path = fname+'.tmp'
	pdf = Pdf.open(fname)
	new_pdf = Pdf.new()
	for page_obj in pdf.pages:
		new_pdf.pages.append(page_obj)
	new_pdf.save(tmp_output_file_path)
	rename(fname, final_input_file_path)
	rename(tmp_output_file_path, fname)
	print(f"Fixed {fname}")



pdfs=O.omeka_get('media',args_dict={'o:media_type':'application/pdf'},retrieve_all=True)
pdf_named_entities={}

'''testbatch=[6941]

pdf_named_entities={p for p in pdf_named_entities if p['o:id'] in testbatch}'''

for m in pdfs:
	
	id=m['o:id']
	print(id)
	parent_id=m['o:item']['o:id']
	#print(id,parent_id)
	
	#first, try to get a transcription from omeka
	if 'bibo:transcriptOf' in m:
		transcription=' '.join([t['@value'] for t in m['bibo:transcriptOf']])
	#then, try to get it from the pdf's text field
	elif m['o:filename'].endswith('.pdf'):
		dl=m['o:original_url']
		response=requests.get(dl,allow_redirects=True)
		open('temp.pdf','wb').write(response.content)
		
		try:
			pdf=PdfFileReader('temp.pdf')
		except:
			preprocess_pdf('temp.pdf')
			pdf=PdfFileReader('temp.pdf')
		#print(dl)
		c=0
		
		numpages=pdf.numPages
		transcription=''
		while c<numpages:
			page=pdf.getPage(c)
			pt=page.extractText()
			transcription+= ' ' +pt
			c+=1
		
		
		if re.fullmatch('\s*',transcription):
			print('no transcript')
			print('fetching transcript...')
			transcription=pdf_to_txt.main('temp.pdf')
		print('writing transcript to media item properties in omeka...')
		O.update_item([{'term':'bibo:transcriptOf','type':'literal','value':transcription}],id,endpoint='media')
		os.remove('temp.pdf')
	else:
		print('NOT A PDF. SKIPPING.')
	#print(transcription)
	
	ne = get_ne(transcription)
	
	
	print(ne)
	#exit()
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

threshold=1

combined=pdf_named_entities

for n in notes_named_entities:
	if n in combined:
		combined[n]=list(set(combined[n]+notes_named_entities[n]))
	else:
		combined[n]=notes_named_entities[n]




combined={i:combined[i] for i in combined if len(combined[i])>=threshold}

d=open('threshold.json','w')
d.write(json.dumps(combined))
d.close()


