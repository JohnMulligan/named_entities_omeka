#!/bin/python3
import os
import re
import json
import requests
import time
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
import entities_to_omeka as eto

app = Flask(__name__,template_folder='./templates/')

m=eto.get_metadata()


@app.route('/<fname>',methods=['POST','GET'])
def main(fname):
	d=open(fname+'.json','r')
	t=d.read()
	d.close()
	raw_entities=json.loads(t)
	print(raw_entities)
	names=[i for i in raw_entities]
	names.sort()
	items=[]
	for name in names:
		items.append({'name':name,'links':raw_entities[name]})
	classes=list(m.keys())
	return render_template('sort.html',
		items=items,
		classes=classes,
		jsonfile=fname
	)

@app.route('/write_entities',methods=['POST'])
def handle():
	ordered_dict=request.form
	fname=ordered_dict['jsonfile']
	d=open(fname+'.json','r')
	t=d.read()
	d.close()
	raw_entities=json.loads(t)
	data=dict()
	excludelist=['jsonfile']
	for o in ordered_dict:
		if o not in excludelist:
			#print(o)
			name,attr=o.split('__')
			if name not in data:
				data[name]={attr:ordered_dict[o]}
			else:
				data[name][attr]=ordered_dict[o]
	#print(data)
	
	out_data={}
	for name in data:
		named=data[name]
		if "OMIT" not in named:
			print(name,named)
			if named['merge-into'] != "":
				out_name=named['merge-into']
				out_class=''
				merge=True
			else:
				if named['rename'] != "":
					out_name=named['rename']
				else:
					out_name=name
				out_class=named["class-select"]
				merge=False
			if out_name in out_data:
				out_data[out_name]['links']+=raw_entities[name]
			else:
				out_data[out_name]={'links':raw_entities[name]}
		
			if merge==False:
				out_data[out_name]['class']=out_class
	print(out_data)
	eto.write_entities(out_data)
	return(out_data)

	
	

if __name__ == "__main__":
	app.run()
