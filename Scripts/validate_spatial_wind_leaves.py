"""Check imported depth and route direction, then inspect fast sideways transport in PIE."""
from build_companion_combat import call,ref,ROOT,OBJ,ASSET,SCENE
import json,time,base64
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools';SM='editor_toolset.toolsets.static_mesh.StaticMeshTools';MI='editor_toolset.toolsets.material_instance.MaterialInstanceTools';OUT=ROOT/'Saved/WoodlandWindFXAudit';F='/Game/Environment/BreezeWoodland'
mesh=ref('/Game/Environment/WoodlandWindFX/SM_SpatialWindLeaves.SM_SpatialWindLeaves');bounds=call('get_bounds',{'mesh':mesh},SM);assert bounds['max']['z']-bounds['min']['z']>450;assert bounds['max']['y']-bounds['min']['y']>2000
report={'bounds':bounds,'directions':{}}
try:
 try:call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','startTransform':{'location':{'x':1850,'y':140,'z':100},'rotation':{'pitch':0,'yaw':180,'roll':0}},'warmupSeconds':0}},APP)
 except RuntimeError as e:
  if 'PIE ended before warmup completed' not in str(e):raise
 assert call('IsPIERunning',{},APP)
 start=time.monotonic();a=call('find_actors',{'name':'Woodland_IntermittentLeaves','tag':'','collision_channels':[]},SCENE)[0];c=call('get_components',{'actor':a,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)[0]
 p=json.loads(call('get_properties',{'instance':c,'properties':['StaticMesh','BodyInstance','bCanEverAffectNavigation']},OBJ));assert p['StaticMesh']==mesh;assert p['BodyInstance']['collisionEnabled']=='NoCollision' and not p['bCanEverAffectNavigation']
 for i,(label,target) in enumerate([('Left',6),('Left',6.6),('Left',7.2),('Right',7.8)]):
  instance=ref(F+'/MI_BreezeLeaves_'+label+'.MI_BreezeLeaves_'+label);sign=call('get_scalar_parameter',{'instance':instance,'name':'WindDirectionSign'},MI);assert sign==(-1 if label=='Left' else 1);report['directions'][label]=sign
  call('set_properties',{'instance':c,'values':json.dumps({'OverrideMaterials':[instance['refPath']]})},OBJ)
  delay=target-(time.monotonic()-start)
  if delay>0:time.sleep(delay)
  capture=call('CaptureEditorImage',{},APP);(OUT/('SpatialLeaves_'+str(i+1)+'_'+label+'.png')).write_bytes(base64.b64decode(capture['data']));print('SPATIAL_LEAF_FRAME',i+1,label,flush=True)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 call('save_assets',{'asset_paths':[]},ASSET);call('set_properties',{'instance':ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),'values':json.dumps({'bThrottleCPUWhenNotForeground':True})},OBJ)
(OUT/'spatial_runtime.json').write_text(json.dumps(report,indent=2));print('SPATIAL_LEAVES_RUNTIME_VERIFIED',flush=True)
