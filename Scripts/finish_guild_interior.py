"""Navigation and safe-hub bounds for the two-storey persistent guild room."""
from build_companion_combat import call,ref,ROOT,SCENE,ASSET,graph
from woodland_fx_graph import props
import json
ACT='editor_toolset.toolsets.actor.ActorTools'
for a in call('find_actors',{'name':'Woodland_NavigationBounds','tag':'','collision_channels':[]},SCENE):
 xf=call('get_actor_transform',{'actor':a},ACT);xf['location']={'x':1525,'y':-3650,'z':350};xf['scale']={'x':30,'y':51,'z':6};call('set_actor_transform',{'actor':a,'xform':xf,'worldspace':True},ACT);props(a,{'bIsSpatiallyLoaded':False})
safe_code='''(fn IsHubLocation (Location)
 (bind (x y z) (Math|Vector|BreakVector Location))
 (return (or
  (and (and (>= x -1100.0) (<= x 1100.0)) (and (>= y -1000.0) (<= y 1000.0)))
  (and (and (>= x -1320.0) (<= x 1320.0)) (and (>= y -8620.0) (<= y -5980.0))))))'''
for bp,output in [('/Game/Game/Combat/BP_CompanionCombat.BP_CompanionCombat','Result'),('/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld','Safe')]:graph(bp,'IsHubLocation',safe_code,[('Location','Vector',None)],[(output,'bool',None)])
for point in json.loads((ROOT/'ContentSource/GuildInterior/npc_spawn_points.json').read_text()):
 name='GuildNPCSpawn_'+point['name'];x,y,z=point['position_m'];found=call('find_actors',{'name':name,'tag':'','collision_channels':[]},SCENE)
 if found:a=found[0]
 else:
  a=call('add_to_scene_from_class',{'actor_type':ref('/Script/Engine.TargetPoint'),'name':name,'xform':{'location':{'x':x*100,'y':-6000-y*100,'z':z*100}}},SCENE);call('set_label',{'actor':a,'label':name},ACT);call('add_tag',{'actor':a,'tag':'GuildNPCSpawn'},ACT)
 props(a,{'bIsSpatiallyLoaded':False});call('set_actor_folder',{'actor':a,'folder_path':'Woodland/Guild Interior/Future NPC Locations'},SCENE)
call('save_assets',{'asset_paths':[]},ASSET);print('GUILD_NAVIGATION_AND_SAFE_HUB_UPDATED',flush=True)
