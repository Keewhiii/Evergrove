from build_companion_combat import *
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
for n in ['Rendering|Material|SetVectorParameterValue','Rendering|Material|SetScalarParameterValue']:
 print(n,call('get_node_type_pins',{'graph':ref(W+':EventGraph'),'type_id':n}))
