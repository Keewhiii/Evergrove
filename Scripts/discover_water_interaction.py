from build_companion_combat import *
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
for word in ['SetVectorParameterValue','GetVelocity']:
 ids=call('find_node_types',{'graph':ref(W+':EventGraph'),'type_id_filter':word,'context_pins':[]})
 print(word,ids)
 for n in ids:
  if 'Collection' in n or 'Velocity' in n:print(n,call('get_node_type_pins',{'graph':ref(W+':EventGraph'),'type_id':n}))
print(call('read_graph_dsl',{'graph':ref(W+':EventGraph')}))
