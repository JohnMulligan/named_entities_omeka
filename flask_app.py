#!/bin/python3
import os
import re
import json
import requests
import time
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from flask_login import login_user,LoginManager,UserMixin,login_required
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

	
	
'''

def get_form_properties(fname):
	d=open(fname,'r')
	t=d.read()
	j=json.loads(t)
	d.close()
	return j['form_properties']

@app.route('/handle_kw_data',methods=['POST'])
def handle_kw_data():
	d=request.form
	db_ops.write_kw_data(d)
	return redirect('/kws')

@app.route('/kws', methods=['POST','GET'])
def kw_sorter():
	kw_stems = db_ops.get_kws()
	kw_stem_form_properties=get_form_properties('kw_stem_form_structure.json')
	return render_template('kw_sort.html',
		kw_stems=kw_stems,
		kw_stem_form_properties=kw_stem_form_properties)

@app.route('/handle_posts_data',methods=['POST'])
def handle_data():
	d=request.form
	db_ops.write_post_data(d)
	return redirect("/")

@app.route('/posts/<POST_ID>', methods=['POST','GET'])
def viewpost(POST_ID):
	paragraphs,post = db_ops.get_post_data(POST_ID)

	return render_template('viewpost.html',
		post=post,
		paragraphs=paragraphs
	)

@app.route('/', methods=['POST','GET'])
def sorter():
	paragraphs,post_data = db_ops.get_post_data()
	paragraph_form_properties = get_form_properties('paragraph_data_structure.json')
	post_form_properties = get_form_properties('post_data_structure.json')
	return render_template('sort.html',
		post_data=post_data,
		paragraphs=paragraphs,
		paragraph_form_properties=paragraph_form_properties,
		post_form_properties=post_form_properties
	)
'''
if __name__ == "__main__":
	app.run()
