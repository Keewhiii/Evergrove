"""Keep trunk collision at the visible trees after the village spacing pass."""
from build_companion_combat import *
PROG='editor_toolset.toolsets.programmatic.ProgrammaticToolset'
settings=ref('/Script/UnrealEd.Default__EditorPerformanceSettings')
call('set_properties',{'instance':settings,'values':json.dumps({'bThrottleCPUWhenNotForeground':False})},OBJ)
script='''import json
def tool(n,a):return execute_tool(n,json.dumps(a))['returnValue']
def find(n):return tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':n,'tag':'','collision_channels':[]})
def run():
 trees=[tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',{'actor':a})['location'] for a in find('Forest_Tree')]
 changed=0
 for a in find('Tree_Trunk'):
  t=tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',{'actor':a});p=t['location']
  candidates=[v for v in trees if abs(v['x']-p['x'])<.01 and v['y']*p['y']>0]
  if not candidates:continue
  tree=min(candidates,key=lambda v:abs(v['y']-p['y']))
  if abs(tree['y']-p['y'])<.01:continue
  p['x']=tree['x'];p['y']=tree['y'];tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',{'actor':a,'xform':t,'worldspace':True});changed+=1
 return {'aligned_trunk_colliders':changed}
'''
print(call('execute_tool_script',{'script':script},PROG),flush=True)
call('save_assets',{'asset_paths':['/Game/Maps/L_EvergroveStart']},ASSET)
call('set_properties',{'instance':settings,'values':json.dumps({'bThrottleCPUWhenNotForeground':True})},OBJ)
