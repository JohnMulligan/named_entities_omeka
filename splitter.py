from PyPDF2 import PdfFileReader, PdfFileWriter
import re
import os
import sys
fname= sys.argv[1]

print(fname)


#get the inputs from the text file
d=open(fname)
t=d.read()
d.close()

ind={}

inputs_dir='input_pdfs'
outputs_dir='output_pdfs'

for l in t.split('\n'):
	
	if l!='':
	
		input_filename,start_page,end_page,output_filename=l.split(',')
		triple=[start_page,end_page,output_filename]
		if input_filename!='':
			if input_filename not in ind:
				ind[input_filename]=[triple]
			else:
				ind[input_filename].append(triple)
print(ind)		

for input_filename in ind:
	pdf=PdfFileReader(os.path.join(inputs_dir,input_filename+'.pdf'))
	
	for i in ind[input_filename]:
		start_page=int(i[0])
		end_page=int(i[1])
		output_filename=i[2]
		pdf_writer=PdfFileWriter()
		for p in range(start_page,end_page+1):
			page=pdf.getPage(p)
			pdf_writer.addPage(page)
			#print(page.extractText())
		output_filename=os.path.join(outputs_dir,output_filename+'.pdf')
		with open(output_filename,'wb') as out:
			pdf_writer.write(out)