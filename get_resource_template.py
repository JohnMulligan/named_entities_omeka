import requests
import json

base_uri='http://10.134.196.127/omeka/api/'

resource_class_templates=json.loads(requests.get(base_uri+'resource_templates').text)

def main():
	classes_and_titles={}
	for t in resource_class_templates:
		t_class_uri=t['o:resource_class']['@id']
		t_class_id=t['o:resource_class']['o:id']
		t_class=json.loads(requests.get(t_class_uri).text)
		t_class_term=t_class['o:term']
		t_class_name=t_class['o:local_name']
		t_property_json=t['o:title_property']
		if t_property_json==None:
			t_property_term='dcterms:title'
			t_property_id=1
			t_property_name='title'
		else:
			t_property_uri=t_property_json['@id']
			t_property_json=json.loads(requests.get(t_property_uri).text)
			t_property_id=t_property_json['o:id']
			t_property_term=t_property_json['o:term']
			t_property_name=t_property_json['o:local_name']
	
		classes_and_titles[t_class_name]={
		'class':{
			'id':t_class_id,
			'name':t_class_name,
			'term':t_class_term
			},
		'property':{
			'id':t_property_id,
			'name':'t_property_name',
			'term':'t_property_term'
			}
		}
	for ct in classes_and_titles:
		print(ct)
		print(classes_and_titles[ct])
	
	return classes_and_titles	