from build_companion_combat import *
ACT='editor_toolset.toolsets.actor.ActorTools'
layout=json.loads((ROOT/'ContentSource/RuralVillage/layout.json').read_text())
call('load_level',{'level_path':'/Game/Maps/L_EvergroveIntro'},SCENE)
for a in call('find_actors',{'name':'RuralNative_TemporaryProbe','tag':'','collision_channels':[]},SCENE):call('remove_from_scene',{'actor':a},SCENE)
call('save_assets',{'asset_paths':['/Game/Maps/L_EvergroveIntro']},ASSET)
call('load_level',{'level_path':'/Game/Maps/L_EvergroveStart'},SCENE)
report={}
for b in layout['buildings']:
 candidates=call('find_actors',{'name':b['name'],'tag':'','collision_channels':[]},SCENE)
 actor=next(a for a in candidates if call('get_label',{'actor':a},ACT)==b['name'])
 t=call('get_actor_transform',{'actor':actor},ACT)
 assert all(abs(t['location'][k]-b['position'][i])<.01 for i,k in enumerate('xyz')),(b,t)
 assert abs(t['rotation']['yaw'])<.01,(b,t)
 report[b['name']]=t
for i,f in enumerate(layout['farms']):
 a=call('find_actors',{'name':'Farm_'+str(i)+'_Soil','tag':'','collision_channels':[]},SCENE)[0];t=call('get_actor_transform',{'actor':a},ACT)
 assert abs(t['location']['x']-f['position'][0])<.01 and abs(t['location']['y']-f['position'][1])<.01 and abs(t['rotation']['yaw'])<.01,(f,t)
 report['farm_'+str(i)]=t
ground=call('find_actors',{'name':'Village_ContinuousGround','tag':'','collision_channels':[]},SCENE)[0]
t=call('get_actor_transform',{'actor':ground},ACT);assert t['location']['z']==-22,t
out=ROOT/'Saved/RuralVillageAudit/persistence.json';out.write_text(json.dumps(report,indent=2))
print('RELOADED_LAYOUT_PERSISTENCE_PASSED',flush=True)
