import json
import omeka_interfacer as O

#this will 
##run through threshold.json
##find EXACT matches between its named entities and existing omeka items' titles
##connect those named entity items to the omeka items

##


d=open('threshold.json','r')
t=d.read()
threshold=json.loads(t)
d.close()

omeka_items=O.basic_search('items',retrieve_all=True)

titles_and_ids={i['o:title']:i['o:id'] for i in omeka_items}

print(titles_and_ids)

titles=[]

titles=[i.lower().strip() for i in titles_and_ids if i!=None]

links={}
for oi in omeka_items:
	oi_id=oi['o:id']
	for pname in oi:
		p=oi[pname]
		if type(p)==list:
			for si in p:
				try:
					if si['type']=='resource':
						if oi_id in links:
							links[oi_id].append(si['value_resource_id'])
						else:
							links[oi_id]=[si['value_resource_id']]
				except:
					pass

print(links)

matches=[]
for t in threshold:
	#print(t)
	
	s=t.lower().strip()
	
	if s in titles:
		matches.append(t)

print(matches)

newmatches={}
for m in matches:
	o_id=titles_and_ids[m]
	match_ids=threshold[m]
	if o_id in links:
		existing_links=links[o_id]
	else:
		existing_links=[]
	new_matches=[i for i in match_ids if i not in existing_links]
	if len(new_matches)>0:
		newmatches[o_id]=new_matches
	
	
print(newmatches)

for self_omeka_id in newmatches:
	print(self_omeka_id)
	for linked_item_id in newmatches[self_omeka_id]:
		print(linked_item_id)
		linked_item_properties=[{'term':'dcterms:references','type':'resource','value':self_omeka_id}]
		self_properties=[{'term':'dcterms:isReferencedBy','type':'resource','value':linked_item_id}]
		O.update_item(self_properties,self_omeka_id,keep_nonlinks=True,keep_links=True)
		O.update_item(linked_item_properties,linked_item_id,keep_nonlinks=True,keep_links=True)

	
	
	
	


