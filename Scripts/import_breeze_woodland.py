"""Import reference foliage and compile intermittent gust/falling-leaf shaders."""
from build_companion_combat import call,ref,ROOT,ASSET,OBJ,SCENE
import json
F='/Game/Environment/BreezeWoodland';SOURCE=ROOT/'ContentSource/BreezeWoodland';OUT=ROOT/'Saved/BreezeWoodlandAudit';OUT.mkdir(exist_ok=True)
SM='editor_toolset.toolsets.static_mesh.StaticMeshTools';MAT='editor_toolset.toolsets.material.MaterialTools';ACT='editor_toolset.toolsets.actor.ActorTools';PROG='editor_toolset.toolsets.programmatic.ProgrammaticToolset'
def props(o,p):return call('set_properties',{'instance':o,'values':json.dumps(p)},OBJ)
props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
for item in json.loads((SOURCE/'manifest.json').read_text()):
 name=item['name'];mesh=ref(F+'/'+name+'.'+name)
 if not call('exists',{'path':F+'/'+name},ASSET):call('import_file',{'folder_path':F,'asset_name':name,'source_file':item['file'],'import_materials':True,'import_textures':True,'combine_meshes':True},SM)
 call('remove_collisions',{'mesh':mesh},SM)
 triangles=call('get_triangle_count',{'mesh':mesh,'lod_index':0},SM)
 if name in ['SM_BreezeLeafField','SM_DirectionalLeafField']:assert 2200<=triangles<=item['triangles'] # Import removes zero-area pixel-outline fan edges.
 else:assert triangles==item['triangles']
 for slot in call('get_material_slots',{'mesh':mesh},SM):
  material='/Game/Environment/LayeredWoodland/'+slot+'.'+slot
  call('set_material',{'mesh':mesh,'slot_name':slot,'material':ref(material)},SM)
 print('IMPORTED',name,flush=True)

class Graph:
 def __init__(self,m):self.m=m
 def n(self,t,**p):
  o=call('add_expression',{'material_or_function':self.m,'expression_class':ref('/Script/Engine.MaterialExpression'+t)},MAT)
  if p:props(o,p)
  return o
 def wire(self,a,b,pin,out=''):
  pins=call('get_expression_input_names',{'expression':b},MAT)
  if pin not in pins:
   if pin=='Input' and pins and pins[0]=='None':pin=''
   else:raise RuntimeError((pin,pins))
  call('connect_expressions',{'from_expression':a,'from_output_name':out,'to_expression':b,'to_input_name':pin},MAT)
 def output(self,a,p,out=''):
  names=call('get_expression_output_names',{'expression':a},MAT)
  if out and out not in names:out=''
  call('connect_to_output',{'expression':a,'output_name':out,'material_property':p},MAT)
 def mul(self,a,value):
  b=self.n('Multiply',ConstB=value);self.wire(a,b,'A');return b
 def add(self,a,value):
  b=self.n('Add',ConstB=value);self.wire(a,b,'A');return b
 def pair(self,t,a,b):
  o=self.n(t);self.wire(a,o,'A');self.wire(b,o,'B');return o
 def vec(self,name,v):return self.n('VectorParameter',ParameterName=name,DefaultValue={'R':v[0],'G':v[1],'B':v[2],'A':1})
 def sine(self,a):
  b=self.n('Sine',Period=1);self.wire(a,b,'Input');return b
 def clamp(self,a):
  b=self.n('Clamp');self.wire(a,b,'Input');return b
 def gust(self,time):
  # Ten-second gust windows separated by a long calm interval, with a softer secondary modulation.
  wave=self.sine(self.mul(time,1/32));envelope=self.clamp(self.mul(self.add(wave,-.35),1/.65))
  strength=self.n('ScalarParameter',ParameterName='WindStrength',DefaultValue=1)
  return self.pair('Multiply',envelope,strength)
 def wind(self,amplitude,height):
  time=self.n('Time');gust=self.pair('Add',self.mul(self.gust(time),1.5),self.n('ScalarParameter',ParameterName='AmbientSway',DefaultValue=.12));pos=self.n('WorldPosition')
  phase=self.pair('DotProduct',pos,self.vec('SpatialPhase',(.0013,.0021,0)))
  fast=self.sine(self.pair('Add',self.mul(time,.7),phase));slow=self.sine(self.pair('Add',self.mul(time,.23),self.mul(phase,1.7)))
  wave=self.pair('Add',fast,self.mul(slow,.45));motion=self.pair('Multiply',wave,gust)
  if height:
   z=self.pair('DotProduct',pos,self.vec('HeightMask',(0,0,1/height)));motion=self.pair('Multiply',motion,self.clamp(z))
  offset=self.pair('Multiply',motion,self.vec('WindDirectionAmplitude',amplitude));self.output(offset,'MP_WorldPositionOffset')
  call('delete_unused_expressions',{'material':self.m},MAT)
  call('recompile',{'material_or_function':self.m},MAT)

for tier in range(5):
 m=ref('/Game/Environment/LayeredWoodland/M_StackedLeaf_'+str(tier)+'.M_StackedLeaf_'+str(tier));Graph(m).wind((8+2*tier,3,1),400)
 print('GUST_SHADER',tier,flush=True)
for path,amp,height in [('/Game/Environment/PixelProps/M_Prop_Grass.M_Prop_Grass',(4,2,0),60),('/Game/Environment/LayeredWoodland/M_LayeredFlowerPixels.M_LayeredFlowerPixels',(2,1,0),120)]:Graph(ref(path)).wind(amp,height)

name='M_BreezeFallingLeaves';m=ref(F+'/'+name+'.'+name)
if not call('exists',{'path':F+'/'+name},ASSET):call('create_material',{'folder_path':F,'asset_name':name},MAT)
for e in call('get_expressions',{'material_or_function':m},MAT):call('delete_expression',{'material_or_function':m,'expression':e},MAT)
g=Graph(m);time=g.n('Time');gust=g.gust(time);uv=g.n('TextureCoordinate');phase=g.n('ComponentMask',R=True,G=False,B=False,A=False);g.wire(uv,phase,'Input')
age=g.n('Frac');g.wire(g.pair('Add',g.mul(time,1/12),phase),age,'Input')
fall=g.pair('Multiply',age,g.vec('FallTravel',(0,0,-510)))
direction=g.n('ScalarParameter',ParameterName='WindDirectionSign',DefaultValue=1)
horizontal=g.pair('Multiply',g.pair('Multiply',age,direction),g.vec('HorizontalTravel',(600,0,0)))
fall=g.pair('Add',fall,horizontal)
flutter=g.sine(g.pair('Add',g.mul(time,.9),g.mul(phase,7)))
drift=g.pair('Multiply',flutter,g.vec('FlutterDistance',(35,16,4)));g.output(g.pair('Add',fall,drift),'MP_WorldPositionOffset')
color=g.n('LinearInterpolate');g.wire(g.vec('LeafShadow',(.065,.21,.025)),color,'A');g.wire(g.vec('LeafHighlight',(.18,.36,.045)),color,'B');g.wire(phase,color,'Alpha');g.output(color,'MP_EmissiveColor')
# Different phase thresholds release individual leaves across the gust rather than one simultaneous sheet.
mask=g.pair('Subtract',gust,g.add(g.mul(phase,.45),.10));g.output(mask,'MP_OpacityMask')
props(m,{'BlendMode':'BLEND_Masked','TwoSided':True,'ShadingModel':'MSM_Unlit','OpacityMaskClipValue':.01});call('recompile',{'material_or_function':m},MAT)
mesh=ref(F+'/SM_DirectionalLeafField.SM_DirectionalLeafField')
for slot in call('get_material_slots',{'mesh':mesh},SM):call('set_material',{'mesh':mesh,'slot_name':slot,'material':m},SM)

script='''import json
def tool(n,a):return execute_tool(n,json.dumps(a))['returnValue']
def run():
 counts={'trees':0,'flowers':0};errors=[]
 for tag in ['WoodlandBlenderArt','PixelWoodland']:
  for a in tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':'','tag':tag,'collision_channels':[]}):
   cs=tool('editor_toolset.toolsets.actor.ActorTools.get_components',{'actor':a,'component_type':{'refPath':'/Script/Engine.StaticMeshComponent'}})
   if not cs:continue
   c=cs[0];p=json.loads(tool('editor_toolset.toolsets.object.ObjectTools.get_properties',{'instance':c,'properties':['StaticMesh']}));path=p['StaticMesh']['refPath'];name=None
   if 'SM_Stacked2D_Tree_' in path or 'SM_BreezeTree_' in path:
    name='SM_BreezeTree_'+path[-1];counts['trees']+=1
   elif 'Flowers' in path:
    name='SM_BreezeFlowers_'+('Yellow' if counts['flowers']%3==0 else 'White');counts['flowers']+=1
   if not name:continue
   xf=tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',{'actor':a});xf['rotation']={'pitch':0,'yaw':0,'roll':0}
   tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',{'actor':a,'xform':xf,'worldspace':True})
   tool('editor_toolset.toolsets.object.ObjectTools.set_properties',{'instance':c,'values':json.dumps({'StaticMesh':'/Game/Environment/BreezeWoodland/'+name+'.'+name,'OverrideMaterials':[]})})
   check=json.loads(tool('editor_toolset.toolsets.object.ObjectTools.get_properties',{'instance':c,'properties':['BodyInstance','bCanEverAffectNavigation']}))
   if check['BodyInstance']['collisionEnabled']!='NoCollision' or check['bCanEverAffectNavigation']:errors.append(a)
 cameras=tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':'Woodland_FollowCamera','tag':'','collision_channels':[]});camera=cameras[0]
 xf=tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',{'actor':camera});xf['rotation']={'pitch':-34,'yaw':-90,'roll':0}
 tool('editor_toolset.toolsets.actor.ActorTools.set_actor_transform',{'actor':camera,'xform':xf,'worldspace':True})
 cc=tool('editor_toolset.toolsets.actor.ActorTools.get_components',{'actor':camera,'component_type':{'refPath':'/Script/Engine.CameraComponent'}})[0]
 tool('editor_toolset.toolsets.object.ObjectTools.set_properties',{'instance':cc,'values':json.dumps({'OrthoWidth':1200})})
 return {'replacements':counts,'collision_errors':errors,'camera_width':1200,'camera_pitch':-34}
'''
report=json.loads(call('execute_tool_script',{'script':script},PROG));assert report['replacements']['trees']==87;assert not report['collision_errors']
actors=call('find_actors',{'name':'Woodland_IntermittentLeaves','tag':'','collision_channels':[]},SCENE)
if not actors:
 actor=call('add_to_scene_from_asset',{'asset_path':F+'/SM_DirectionalLeafField','name':'Woodland_IntermittentLeaves','xform':{'location':{'x':0,'y':0,'z':0},'rotation':{'pitch':0,'yaw':0,'roll':0},'scale':{'x':1,'y':1,'z':1}},'snap_to_ground':False},SCENE)
 call('set_label',{'actor':actor,'label':'Woodland_IntermittentLeaves'},ACT)
else:actor=actors[0]
component=call('get_components',{'actor':actor,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)[0]
props(component,{'bUseDefaultCollision':False,'BodyInstance':{'CollisionProfileName':'NoCollision','CollisionEnabled':'NoCollision'},'bCanEverAffectNavigation':False,'CastShadow':False,'BoundsScale':2})
props(actor,{'bIsSpatiallyLoaded':False})
call('save_assets',{'asset_paths':[]},ASSET);report['falling_leaves']=220;report['gust_period_seconds']=32
(OUT/'migration.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
