"""World-space, limited-palette ground detail without realistic noise or normal maps."""
from build_companion_combat import call,ref,ROOT,ASSET,OBJ,SCENE
from woodland_fx_graph import Graph,props,MAT
import json
ACT='editor_toolset.toolsets.actor.ActorTools';PROG='editor_toolset.toolsets.programmatic.ProgrammaticToolset'
F='/Game/Environment/CartoonGround'
def linear(c):
 c/=255;return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
def material(name,palette,road=False):
 m=ref(F+'/'+name+'.'+name)
 if not call('exists',{'path':F+'/'+name},ASSET):call('create_material',{'folder_path':F,'asset_name':name},MAT)
 for e in call('get_expressions',{'material_or_function':m},MAT):call('delete_expression',{'material_or_function':m,'expression':e},MAT)
 g=Graph(m);world=g.mask(g.n('WorldPosition'),'RG')
 def hash_at(size,seed):
  cell=g.n('Floor');g.wire(g.mul(world,1/size),cell,'Input')
  dot=g.pair('DotProduct',cell,g.vec('HashAxis'+str(seed),(12.9898+seed,78.233-seed,0)))
  frac=g.n('Frac');g.wire(g.mul(g.sine(dot,6.283185),43758.5453),frac,'Input');return frac
 def step(v,t):
  return g.clamp(g.mul(g.add(v,-t),10000))
 def mix(a,b,t):
  n=g.n('LinearInterpolate');g.wire(a,n,'A');g.wire(b,n,'B');g.wire(t,n,'Alpha');return n
 cs=[g.vec('Palette'+str(i),tuple(linear(v) for v in rgb)) for i,rgb in enumerate(palette)]
 broad=hash_at(72 if road else 96,1);detail=hash_at(7 if road else 8,2)
 # Broad clustered variation, tiny sparse painted marks, no continuous photoreal noise.
 color=mix(cs[0],cs[1],g.mul(step(broad,.52),.55));color=mix(color,cs[2],g.mul(step(broad,.82),.55))
 speck=g.pair('Multiply',step(detail,.91 if road else .965),step(hash_at(36,3),.48))
 color=mix(color,cs[3],g.mul(speck,.7))
 # Subtle compressed earth/grassy color patches at the intermediate scale.
 color=mix(color,cs[2],g.mul(step(hash_at(22,4),.88),.18))
 g.output(color,'MP_BaseColor');g.output(g.n('Constant',R=1),'MP_Roughness');g.output(g.n('Constant',R=0),'MP_Specular')
 props(m,{'TwoSided':True,'ShadingModel':'MSM_DefaultLit'});call('recompile',{'material_or_function':m},MAT);return m
grass=material('M_PaintedGrass',[(76,132,43),(89,146,49),(66,119,40),(116,158,60)])
road=material('M_PaintedRoad',[(184,138,65),(198,153,78),(168,120,57),(220,178,103)],True)
script='''import json
def tool(n,a):return execute_tool(n,json.dumps(a))['returnValue']
def run():
 changed=[]
 for a in tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':'','tag':'','collision_channels':[]}):
  cs=tool('editor_toolset.toolsets.actor.ActorTools.get_components',{'actor':a,'component_type':{'refPath':'/Script/Engine.StaticMeshComponent'}})
  for c in cs:
   p=json.loads(tool('editor_toolset.toolsets.object.ObjectTools.get_properties',{'instance':c,'properties':['StaticMesh','OverrideMaterials']}));mesh=p.get('StaticMesh',{}).get('refPath','');mats=str(p.get('OverrideMaterials',[]))
   ground='SM_Pixel_Ground' in mesh or 'M_Woodland_Meadow' in mats or 'M_Woodland_Forest' in mats
   path='M_Woodland_Path' in mats or 'SM_Woodland_TrailSkin' in mesh or 'SM_Pixel_Trail' in mesh
   if ground or path:
    material='/Game/Environment/CartoonGround/'+('M_PaintedGrass.M_PaintedGrass' if ground else 'M_PaintedRoad.M_PaintedRoad')
    tool('editor_toolset.toolsets.object.ObjectTools.set_properties',{'instance':c,'values':json.dumps({'OverrideMaterials':[material]})});changed.append({'component':c,'before':p,'surface':'grass' if ground else 'road'})
 return {'changed':changed}
'''
out=ROOT/'Saved/GuildInteriorAudit';out.mkdir(exist_ok=True);report=call('execute_tool_script',{'script':script},PROG)
if not (out/'ground_before.json').exists():(out/'ground_before.json').write_text(report)
call('save_assets',{'asset_paths':[]},ASSET);print('CARTOON_GROUND_UPDATED',len(json.loads(report)['changed']),flush=True)
