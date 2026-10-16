from build_companion_combat import *
M='/Game/Game/UI/BP_EvergroveIntroHUD.BP_EvergroveIntroHUD'
bindings=[('Up','MenuUp'),('W','MenuUp'),('Down','MenuDown'),('S','MenuDown'),('Left','MenuLeft'),('A','MenuLeft'),('Right','MenuRight'),('D','MenuRight'),('Enter','Activate'),('SpaceBar','Activate'),('Escape','Back')]
for name,action in [('MenuUp','(CallFunction|MoveSelection :Step -1)'),('MenuDown','(CallFunction|MoveSelection :Step 1)'),('MenuLeft','(CallFunction|AdjustOption :Step -1)'),('MenuRight','(CallFunction|AdjustOption :Step 1)')]:graph(M,name,f'(fn {name} () {action})')
g=ref(M+':EventGraph')
for i,(key,method) in enumerate(bindings):
 event=call('create_node',{'graph':g,'type_id':'Input|KeyboardEvents|'+key,'pos':{'x':0,'y':1400+i*180}})
 action=call('create_node',{'graph':g,'type_id':'CallFunction|'+method,'pos':{'x':350,'y':1400+i*180}})
 a,b=call('get_node_infos',{'nodes':[event,action]})
 call('connect_pins',{'output_pin':next(p['pin_id'] for p in a['output_pins'] if p['name']=='Pressed'),'input_pin':next(p['pin_id'] for p in b['input_pins'] if p['name']=='execute')})
call('compile_blueprint',{'blueprint':ref(M),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[]},ASSET)
print('INTRO_COMPILED_AND_SAVED',flush=True)
