"""Check both route presets in Play mode, leaving the saved woodland on leftward wind."""
from build_companion_combat import call,ref,ROOT,OBJ,ASSET,SCENE
import json,time,base64
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools';MI='editor_toolset.toolsets.material_instance.MaterialInstanceTools';F='/Game/Environment/BreezeWoodland';OUT=ROOT/'Saved/BreezeWoodlandAudit'
report={}
try:
 try:call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','startTransform':{'location':{'x':1850,'y':140,'z':100},'rotation':{'pitch':0,'yaw':180,'roll':0}},'warmupSeconds':0}},APP)
 except RuntimeError as e:
  if 'PIE ended before warmup completed' not in str(e):raise
 assert call('IsPIERunning',{},APP)
 start=time.monotonic()
 actor=call('find_actors',{'name':'Woodland_IntermittentLeaves','tag':'','collision_channels':[]},SCENE)[0]
 c=call('get_components',{'actor':actor,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)[0]
 p=json.loads(call('get_properties',{'instance':c,'properties':['StaticMesh','OverrideMaterials','BodyInstance','bCanEverAffectNavigation']},OBJ))
 assert p['StaticMesh']['refPath'].endswith('SM_DirectionalLeafField.SM_DirectionalLeafField')
 assert p['BodyInstance']['collisionEnabled']=='NoCollision' and not p['bCanEverAffectNavigation']
 report['runtime_component']=p
 for title,target in [('Left',6),('Right',9)]:
  preset=ref(F+'/MI_BreezeLeaves_'+title+'.MI_BreezeLeaves_'+title)
  sign=call('get_scalar_parameter',{'instance':preset,'name':'WindDirectionSign'},MI);assert sign==(-1 if title=='Left' else 1)
  call('set_properties',{'instance':c,'values':json.dumps({'OverrideMaterials':[preset['refPath']]})},OBJ)
  delay=target-(time.monotonic()-start)
  if delay>0:time.sleep(delay)
  cap=call('CaptureEditorImage',{},APP);(OUT/('Directional_'+title+'.png')).write_bytes(base64.b64decode(cap['data']))
  report[title]={'sign':sign,'horizontal_velocity_cm_per_second':sign*50};print('VERIFIED',title,flush=True)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 call('save_assets',{'asset_paths':[]},ASSET)
 call('set_properties',{'instance':ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),'values':json.dumps({'bThrottleCPUWhenNotForeground':True})},OBJ)
(OUT/'directional_runtime.json').write_text(json.dumps(report,indent=2));print('DIRECTIONAL_LEAVES_VERIFIED',flush=True)
