import json
import requests
import sys
from PyPDF2 import PdfFileReader, PdfFileWriter
import re
import os
import pdf_to_txt
import omeka_interfacer as O
import string


d=open('test.txt','r')
text=d.read()
d.close()
print(text)


punctuation='!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~¿¡'
text=re.sub('['+punctuation+']+',' ',text)
text=re.sub('\n+',' ',text)
text=re.sub('\s+',' ',text)

joiners=re.compile("(de|da|do|das|dos|a|o|de la|del|de las|de los|la|el|du|de l\'|des|le)")
proper=re.compile('[A-ZÀÁÃÂÉÊÍÓÔÕÚÜÇ][a-zàáãâéêíóôõúüçéàèùâêîôûáéíóúüñ]+')

known_baddies=['The','However','While','But','Is','Can','How','Na','Do','Com','Como','Desta','Até','Ha','Este']

tokenized=text.split(' ')
allmatches=[]
runningmatch=[]
c=0
while c<len(tokenized):
	while True:
		t=tokenized[c]
		c+=1
		if re.fullmatch(proper,t) and t not in known_baddies:
			runningmatch.append(t)
		elif re.fullmatch(joiners,t) and len(runningmatch)>0:
			runningmatch.append(t)
		else:
			
			if len(runningmatch)>0:
				while re.fullmatch(joiners,runningmatch[-1]):
					del(runningmatch[-1])
				allmatches.append(' '.join(runningmatch))
			runningmatch=[]
			break

PN=list(set(allmatches))




#print(PN)
maximal=[]
for n in PN:
	skip=False
	for o in PN:
		if n in o and n!=o:
			print(n,o)
			skip=True
	if skip==False:
		maximal.append(n)
print(maximal)