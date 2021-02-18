import fitz
from PIL import Image
import os
import pytesseract

def main(fn,jpg_dir='jpg_dir'):

	jpg_dir=jpg_dir
	doc = fitz.open(fn)

	if not os.path.exists(jpg_dir):
		os.mkdir(jpg_dir)


	#borrowed from https://stackoverflow.com/questions/2693820/extract-images-from-pdf-without-resampling-in-python?lq=1
	for i in range(len(doc)):
		print(i)
		for img in doc.getPageImageList(i):
			try:
				xref = img[0]
				pix = fitz.Pixmap(doc, xref)
				output_filename = "%s-%s.jpg" % (i, xref)
				output_filepath = os.path.join(jpg_dir,output_filename)
				print(output_filepath)

				pix = fitz.Pixmap(fitz.csRGB, pix)
				img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
				img.save(output_filepath,"JPEG")

				pix = None
			except:
				print('bad page')
	transcription=''
	for i in os.listdir(jpg_dir):
		fp =os.path.join(jpg_dir,i)
		t=pytesseract.image_to_string(Image.open(fp))
		transcription+=t
		print(t)
		os.remove(fp)
	os.rmdir(jpg_dir)
	return transcription
	
	