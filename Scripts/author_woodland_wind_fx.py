"""Always-on subtle sway, visible gusts, and speed/proximity-triggered leaf bursts."""
from build_companion_combat import call,ref,ROOT,ASSET,OBJ,SCENE,graph,var,create
from woodland_fx_graph import Graph,props,MAT
import json
F='/Game/Environment/WoodlandWindFX';SM='editor_toolset.toolsets.static_mesh.StaticMeshTools';ACT='editor_toolset.toolsets.actor.ActorTools';PROG='editor_toolset.toolsets.programmatic.ProgrammaticToolset';WORLD='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld';BURST='/Game/Game/World/BP_RunLeafBurst.BP_RunLeafBurst'
props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
for item in json.loads((ROOT/'ContentSource/WoodlandWindFX/manifest.json').read_text()):
 if not call('exists',{'path':F+'/'+item['name']},ASSET):call('import_file',{'folder_path':F,'asset_name':item['name'],'source_file':item['file'],'import_materials':False,'import_textures':False,'combine_meshes':True},SM)
 call('remove_collisions',{'mesh':ref(F+'/'+item['name']+'.'+item['name'])},SM)
def material(name):
 m=ref(F+'/'+name+'.'+name)
 if not call('exists',{'path':F+'/'+name},ASSET):call('create_material',{'folder_path':F,'asset_name':name},MAT)
 for e in call('get_expressions',{'material_or_function':m},MAT):call('delete_expression',{'material_or_function':m,'expression':e},MAT)
 return m,Graph(m)
def assign(mesh,mat):
 for slot in call('get_material_slots',{'mesh':mesh},SM):call('set_material',{'mesh':mesh,'slot_name':slot,'material':mat},SM)

# A leaf starts at its bush, springs outward/up, then falls back down. Each actor supplies its own birth time.
m,g=material('M_RunLeafBurst');time=g.n('Time');birth=g.n('ScalarParameter',ParameterName='BurstStartTime',DefaultValue=0,bUseCustomPrimitiveData=True,PrimitiveDataIndex=0)
age=g.clamp(g.mul(g.pair('Subtract',time,birth),1/1.25));uv=g.n('TextureCoordinate');phase=g.mask(uv,'R')
x=g.sine(phase);y=g.sine(g.add(phase,.25));horizontal=g.n('AppendVector');g.wire(x,horizontal,'A');g.wire(y,horizontal,'B');direction=g.n('AppendVector');g.wire(horizontal,direction,'A');g.wire(g.n('Constant',R=0),direction,'B')
travel=g.pair('Multiply',direction,g.mul(age,105));height=g.pair('Add',g.mul(age,260),g.mul(g.pair('Multiply',age,age),-330));vertical=g.pair('Multiply',height,g.vec('UpAxis',(0,0,1)))
g.output(g.pair('Add',travel,vertical),'MP_WorldPositionOffset');color=g.n('LinearInterpolate');g.wire(g.vec('LeafShadow',(.035,.16,.025)),color,'A');g.wire(g.vec('LeafHighlight',(.15,.32,.045)),color,'B');g.wire(phase,color,'Alpha');g.output(color,'MP_EmissiveColor')
props(m,{'TwoSided':True,'ShadingModel':'MSM_Unlit'});call('recompile',{'material_or_function':m},MAT)
mesh=ref(F+'/SM_RunLeafBurst.SM_RunLeafBurst');assign(mesh,m);props(mesh,{'PositiveBoundsExtension':{'x':120,'y':120,'z':100},'NegativeBoundsExtension':{'x':120,'y':120,'z':100}})

# Pale, translucent curls sweep sideways only while the gust envelope is active.
m,g=material('M_VisibleWind');time=g.n('Time');uv=g.n('TextureCoordinate');phase=g.mask(uv,'R');along=g.mask(uv,'G');age=g.n('Frac');g.wire(g.pair('Add',g.mul(time,.18),phase),age,'Input');sign=g.n('ScalarParameter',ParameterName='WindDirectionSign',DefaultValue=-1)
travel=g.pair('Multiply',g.pair('Multiply',age,sign),g.vec('WindTravel',(1800,0,0)));g.output(travel,'MP_WorldPositionOffset')
fade=g.pair('Multiply',g.sine(age,2),g.sine(along,2));opacity=g.mul(g.pair('Multiply',g.gust(time),fade),.85);g.output(opacity,'MP_Opacity');g.output(g.vec('WindTint',(.65,.78,.67)),'MP_EmissiveColor')
props(m,{'BlendMode':'BLEND_Translucent','TwoSided':True,'ShadingModel':'MSM_Unlit'});call('recompile',{'material_or_function':m},MAT)
mesh=ref(F+'/SM_FluidWindRibbonLocal.SM_FluidWindRibbonLocal');assign(mesh,m)
actors=call('find_actors',{'name':'Woodland_VisibleWind','tag':'','collision_channels':[]},SCENE)
if actors:a=actors[0]
else:
 a=call('add_to_scene_from_asset',{'asset_path':F+'/SM_FluidWindRibbonLocal','name':'Woodland_VisibleWind','xform':{'location':{'x':0,'y':0,'z':0}},'snap_to_ground':False},SCENE);call('set_label',{'actor':a,'label':'Woodland_VisibleWind'},ACT)
c=call('get_components',{'actor':a,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)[0];props(c,{'StaticMesh':mesh['refPath'],'Mobility':'Movable','bUseDefaultCollision':False,'BodyInstance':{'CollisionProfileName':'NoCollision','CollisionEnabled':'NoCollision'},'bCanEverAffectNavigation':False,'CastShadow':False,'BoundsScale':2});props(a,{'bIsSpatiallyLoaded':False});call('add_tag',{'actor':a,'tag':'WoodlandWindVisual'},ACT)

# Preserve the existing spatial variation, but add a small baseline and amplify gusts.
for i in range(5):
 mat=ref('/Game/Environment/LayeredWoodland/M_StackedLeaf_'+str(i)+'.M_StackedLeaf_'+str(i));expressions=call('get_expressions',{'material_or_function':mat},MAT);g=Graph(mat);parameters={}
 for e in expressions:
  if 'ScalarParameter' in str(call('get_class',{'instance':e},OBJ)):
   p=json.loads(call('get_properties',{'instance':e,'properties':['ParameterName']},OBJ));parameters[p['ParameterName']]=e
 if 'AmbientSway' in parameters:continue
 strength=parameters['WindStrength'];gust=None
 for e in expressions:
  if 'Multiply' not in str(call('get_class',{'instance':e},OBJ)):continue
  if any(p['expression']==strength for p in call('get_expression_inputs',{'material_or_function':mat,'expression':e},MAT)):gust=e;break
 assert gust
 target=None
 for e in expressions:
  if 'Multiply' not in str(call('get_class',{'instance':e},OBJ)):continue
  for pin in call('get_expression_inputs',{'material_or_function':mat,'expression':e},MAT):
   if pin['expression']==gust:target=(e,pin['input_name'])
 assert target
 baseline=g.n('ScalarParameter',ParameterName='AmbientSway',DefaultValue=.12);envelope=g.pair('Add',g.mul(gust,1.5),baseline);g.wire(envelope,target[0],target[1]);call('recompile',{'material_or_function':mat},MAT);print('CONTINUOUS_SWAY',i,flush=True)

create(BURST,'/Script/Engine.Actor')
graph(BURST,'EventGraph','''(event EventBeginPlay
 (bind leaf (AddComponent|Common|AddStaticMeshComponent :RelativeTransform (Math|Transform|MakeTransform)))
 (Components|StaticMesh|SetStaticMesh :self leaf :NewMesh "/Game/Environment/WoodlandWindFX/SM_RunLeafBurst.SM_RunLeafBurst")
 (Collision|SetCollisionEnabled :self leaf :NewType "NoCollision")
 (Rendering|Material|SetCustomPrimitiveDataFloat :self leaf :DataIndex 0 :Value (Utilities|Time|GetGameTimeInSeconds))
 (Actor|SetLifeSpan :InLifespan 1.25))''')

script='''import json
def tool(n,a):return execute_tool(n,json.dumps(a))['returnValue']
def run():
 centers=[]
 for tag in ['WoodlandBlenderArt','PixelWoodland']:
  for a in tool('editor_toolset.toolsets.scene.SceneTools.find_actors',{'name':'','tag':tag,'collision_channels':[]}):
   cs=tool('editor_toolset.toolsets.actor.ActorTools.get_components',{'actor':a,'component_type':{'refPath':'/Script/Engine.StaticMeshComponent'}})
   if not cs:continue
   p=json.loads(tool('editor_toolset.toolsets.object.ObjectTools.get_properties',{'instance':cs[0],'properties':['StaticMesh','bVisible','bHiddenInGame']}));path=p['StaticMesh']['refPath']
   if p['bVisible'] and not p['bHiddenInGame'] and ('SM_BroadleafGrass' in path or 'SM_Prop_Bush' in path):
    pos=tool('editor_toolset.toolsets.actor.ActorTools.get_actor_transform',{'actor':a})['location'];centers.append(pos)
 return {'centers':centers}
'''
centers=json.loads(call('execute_tool_script',{'script':script},PROG))['centers']
for x,y in [(-820,440),(-700,680),(710,630),(820,-550),(1330,-670),(1450,660),(1690,810),(2030,780),(2100,-820),(1600,-850)]:
 centers.extend([{'x':x,'y':y,'z':3},{'x':x+90,'y':y+30,'z':3}])
var(WORLD,'GrassLeafCenters','Vector','ARRAY');call('set_variable_instance_editable',{'blueprint':ref(WORLD),'variable_name':'GrassLeafCenters','instance_editable':True})
for name,typ in [('GrassLeafCheckAt','float'),('GrassLeafBurstAt','float'),('GrassLeafBurstThisStep','bool'),('GrassLeafBurstCount','int')]:var(WORLD,name,typ)
graph(WORLD,'UpdateGrassLeafBursts','''(fn UpdateGrassLeafBursts ()
 (bind now (Utilities|Time|GetGameTimeInSeconds))
 (if (< now (Variables|Default|GetGrassLeafCheckAt)) (return))
 (Variables|Default|SetGrassLeafCheckAt (+ now 0.08))
 (if (< now (Variables|Default|GetGrassLeafBurstAt)) (return))
 (if (< (Variables|Default|GetGrassMoveEnergy) 0.55) (return))
 (bind player (Game|GetPlayerCharacter 0))
 (if (not (CallFunction|Valid :Object player)) (return))
 (if (< (Math|Vector|VectorLengthXY (Transformation|GetVelocity :self player)) 330.0) (return))
 (Variables|Default|SetGrassLeafBurstThisStep false)
 (for center (Variables|Default|GetGrassLeafCenters)
  (if (not (Variables|Default|GetGrassLeafBurstThisStep))
   (if (< (Math|Vector|VectorLengthXY (- center (Transformation|GetActorLocation :self player))) 95.0)
    (Game|SpawnActorfromClass :Class "/Game/Game/World/BP_RunLeafBurst.BP_RunLeafBurst_C" :SpawnTransform (Math|Transform|MakeTransform :Location (+ center (Math|Vector|MakeVector 0.0 0.0 35.0)) :Scale (Math|Vector|MakeVector 1.4 1.4 1.4)) :CollisionHandlingOverride "AlwaysSpawn")
    (Variables|Default|SetGrassLeafBurstAt (+ now 0.22))
    (Variables|Default|SetGrassLeafBurstThisStep true)
    (Variables|Default|SetGrassLeafBurstCount (+ (Variables|Default|GetGrassLeafBurstCount) 1))))))''')
props(ref(WORLD.split('.')[0]+'.Default__BP_WoodlandWorld_C'),{'GrassLeafCenters':centers})
for a in call('find_actors',{'name':'','actor_type':ref(WORLD+'_C'),'tag':'','collision_channels':[]},SCENE):props(a,{'GrassLeafCenters':centers})
source=(ROOT/'Saved/CombatAudit/UpdateGrassInteraction.dsl').read_text(encoding='utf-8')
if '(CallFunction|UpdateGrassLeafBursts)' not in source:source=source.rstrip()[:-1]+'\n (CallFunction|UpdateGrassLeafBursts))'
graph(WORLD,'UpdateGrassInteraction',source,[('Delta','float',None)])
var(WORLD,'VisibleWindActor','/Script/Engine.Actor')
graph(WORLD,'UpdateVisibleWind','''(fn UpdateVisibleWind ()
 (if (not (CallFunction|Valid :Object (Variables|Default|GetVisibleWindActor)))
  (for wind (Actor|GetAllActorswithTag :Tag "WoodlandWindVisual") (Variables|Default|SetVisibleWindActor wind)))
 (bind player (Game|GetPlayerCharacter 0))
 (if (and (CallFunction|Valid :Object player) (CallFunction|Valid :Object (Variables|Default|GetVisibleWindActor)))
  (bind (x y z) (Math|Vector|BreakVector (Transformation|GetActorLocation :self player)))
  (Rendering|SetActorHiddenInGame :self (Variables|Default|GetVisibleWindActor) :bNewHidden (< y -5000.0))
  (Transformation|SetActorLocation :self (Variables|Default|GetVisibleWindActor) :NewLocation (Math|Vector|MakeVector 2000.0 0.0 0.0) :bTeleport true)))''')
source=(ROOT/'Saved/CombatAudit/UpdateCamera.dsl').read_text(encoding='utf-8')
if '(CallFunction|UpdateVisibleWind)' not in source:source=source.replace('(fn UpdateCamera (Delta)','(fn UpdateCamera (Delta)\n (CallFunction|UpdateVisibleWind)',1)
graph(WORLD,'UpdateCamera',source,[('Delta','float',None)])
call('save_assets',{'asset_paths':[]},ASSET)
import runpy
runpy.run_path(str(ROOT/'Scripts/apply_fluid_wind.py'),run_name='__main__')
if (ROOT/'ContentSource/WoodlandWindFX/spatial_leaves_manifest.json').exists():runpy.run_path(str(ROOT/'Scripts/apply_spatial_wind_leaves.py'),run_name='__main__')
out=ROOT/'Saved/WoodlandWindFXAudit';out.mkdir(exist_ok=True);(out/'authoring.json').write_text(json.dumps({'vegetation_centers':len(centers),'burst_leaves':8,'burst_lifetime':1.25,'run_threshold':330,'burst_radius':95,'baseline_sway':.12,'gust_multiplier':1.5,'wind_ribbons':6},indent=2));print('WOODLAND_WIND_FX_AUTHORED',len(centers),flush=True)
