import omeka_interfacer as O
import json
import requests
import sys


omeka_credentials,base_url,base_path=O.get_credentials()

#get key metadata on the resource class templates
def get_metadata():
	resource_class_templates=O.omeka_get('resource_templates')
	classes_and_titles={}
	for t in resource_class_templates:
		t_class_uri=t['o:resource_class']['@id']
		t_class_id=t['o:resource_class']['o:id']
		t_class=json.loads(requests.get(t_class_uri).text)
		t_name=t['o:label']
		t_id=t['o:id']
		t_class_term=t_class['o:term']
		t_class_name=t['o:label']
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
			'name':t_property_name,
			'term':t_property_term
			},
		'template':{
			'id':t_id,
			'name':t_name
			}
		}
	return classes_and_titles
	
classes_and_titles=get_metadata()

#this will take the json from the processed entities, and write them to omeka
#should come in the form {item_title:{'links':[item_ids],'class':resource_class_name}}
#type is either "media" or "item"

def write_entities(entities):

	'''d=open('test.json','r')
	t=d.read()
	entities=json.loads(t)
	d.close()'''

	for title in entities:
		try:
			linked_ids=entities[title]['links']
			rclass=entities[title]['class']
			rclass_id=classes_and_titles[rclass]['class']['id']
			rclass_term=classes_and_titles[rclass]['class']['term']
			titleprop=classes_and_titles[rclass]['property']
			template=classes_and_titles[rclass]['template']
			template_id=template['id']
			rclass_props=[{'term':titleprop['term'],'value':title,'type':'literal'}]
			native_props={'o:resource_template':template_id}
			self_omeka_id=O.create_item(rclass_props,native_properties=native_props,item_class=rclass_term)
			#resource_class_id=O.omeka_get('resource_classes',{'term':rclass_term})[0]['o:id']
	
			'''#omeka privileges linking between items, not media
			#if we're dealing with links back to media, map these to their parent items instead
			if type=='media':
				prent_item_ids=[]
				for link in links:
					link_data=O.omeka_basic('media',{'o:id':link_id})
					parent_item_id=link_data['o:item']['o:id']
					parent_item_ids.append(parent_item_id)
				linked_ids=parent_item_ids'''
			linked_ids=list(set(linked_ids))
	
			print(linked_ids)
	
			for linked_item_id in linked_ids:
				linked_item_properties=[{'term':'dcterms:references','type':'resource','value':self_omeka_id}]
				self_properties=[{'term':'dcterms:isReferencedBy','type':'resource','value':linked_item_id}]
				O.update_item(self_properties,self_omeka_id)
				O.update_item(linked_item_properties,linked_item_id)
		except:
			print('error with',title,entities[title])





'''
omeka_id=O.update_item(item_properties,parent_item_omeka_id)
parent_item_omeka_id=O.create_item(item_properties,class_map['default_class'])
resource_class_id=O.basic_search('resource_classes',{'term':'bibo:Note'})[0]['o:id']
notes=O.basic_search('items',args_dict={'resource_class_id':resource_class_id},retrieve_all=True)
notes_named_entities={}

'o:item':'o:id'
'''
