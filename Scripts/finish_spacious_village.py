from build_companion_combat import *
PROG='editor_toolset.toolsets.programmatic.ProgrammaticToolset'
layout=json.loads((ROOT/'ContentSource/RuralVillage/layout.json').read_text())
guild=layout['buildings'][0]['position']
script='''import json
def tool(n,a):return execute_tool(n,json.dumps(a))['returnValue']
def find(n):return tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':n,'tag':'','collision_channels':[]})
def put(a,t):return tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',{'actor':a,'xform':t,'worldspace':True})
def run():
 for a in find('Tree_Trunk')+tool('editor_toolset.toolsets.scene.SceneTools.get_actors_in_folder',{'folder_path':'Wildflowers'}):
  t=tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',{'actor':a});p=t['location']
  if p['x']<1000:p['x']=780+(p['x']-780)*1.35;p['y']*=1.35;put(a,t)
 for a in find('VillageGuildSign'):put(a,{'location':{'x':GX,'y':GY+375,'z':370},'rotation':{'pitch':0,'yaw':90,'roll':0},'scale':{'x':1,'y':1,'z':1}})
 for a in find('Village_Path_10'):
  t=tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',{'actor':a})
  if abs(t['location']['x']+995.25)<2:
   t['location']['y']=135;t['rotation']['yaw']=180;put(a,t)
 for a in find('NavMeshBoundsVolume'):
  t=tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',{'actor':a})
  if t['location']['y']>-5000:t['location']={'x':200,'y':0,'z':280};t['scale']={'x':95,'y':70,'z':6};put(a,t)
 return {'aligned':True}
'''.replace('GX',str(guild[0])).replace('GY',str(guild[1]))
print(call('execute_tool_script',{'script':script},PROG),flush=True)
call('save_assets',{'asset_paths':['/Game/Maps/L_EvergroveStart']},ASSET)
