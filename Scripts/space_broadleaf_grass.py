"""Use fewer larger overlapping clumps so broad leaf shapes stay readable in gameplay."""
from build_companion_combat import call,ROOT
import json
script='''import json
def tool(n,a):return execute_tool(n,json.dumps(a))['returnValue']
def run():
 shown=0;hidden=0
 for a in tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':'','tag':'PixelWoodland','collision_channels':[]}):
  label=tool('editor_toolset.toolsets.actor.ActorTools.get_label',{'actor':a})
  if 'GrassPatch_' not in label and 'BorderGrass_' not in label:continue
  bits=label.split('_');row=int(bits[-2]);col=int(bits[-1]);show=row%2==0 and col%2==0
  c=tool('editor_toolset.toolsets.actor.ActorTools.get_components',{'actor':a,'component_type':{'refPath':'/Script/Engine.StaticMeshComponent'}})[0]
  tool('editor_toolset.toolsets.object.ObjectTools.set_properties',{'instance':c,'values':json.dumps({'bVisible':show,'bHiddenInGame':not show})})
  if show:
   xf=tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',{'actor':a});s=1.6 if 'GrassPatch_' in label else 1.36;xf['scale']={'x':s,'y':s,'z':s}
   tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',{'actor':a,'xform':xf,'worldspace':True});shown+=1
  else:hidden+=1
 tool('editor_toolset.toolsets.asset.AssetTools.save_assets',{'asset_paths':[]})
 return {'large_patch_border_clumps':shown,'redundant_small_clumps_hidden':hidden,'scale':1.6}
'''
report=json.loads(call('execute_tool_script',{'script':script},'editor_toolset.toolsets.programmatic.ProgrammaticToolset'));(ROOT/'Saved/BroadleafGrassAudit/readability.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
