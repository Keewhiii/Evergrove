"""Capture several actual Play mode frames to inspect evolving wind curls."""
from build_companion_combat import call,ref,ROOT,OBJ,ASSET,SCENE
import json,time,base64
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools';OUT=ROOT/'Saved/WoodlandWindFXAudit'
try:
 try:call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','startTransform':{'location':{'x':1850,'y':140,'z':100},'rotation':{'pitch':0,'yaw':180,'roll':0}},'warmupSeconds':0}},APP)
 except RuntimeError as e:
  if 'PIE ended before warmup completed' not in str(e):raise
 assert call('IsPIERunning',{},APP)
 start=time.monotonic();a=call('find_actors',{'name':'Woodland_VisibleWind','tag':'','collision_channels':[]},SCENE)[0]
 c=call('get_components',{'actor':a,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)[0]
 p=json.loads(call('get_properties',{'instance':c,'properties':['StaticMesh','BodyInstance','bCanEverAffectNavigation']},OBJ));assert 'SM_FluidWindRibbonLocal' in p['StaticMesh']['refPath'];assert p['BodyInstance']['collisionEnabled']=='NoCollision' and not p['bCanEverAffectNavigation']
 for i,target in enumerate([6,6.7,7.4,8.1]):
  delay=target-(time.monotonic()-start)
  if delay>0:time.sleep(delay)
  cap=call('CaptureEditorImage',{},APP);(OUT/('FluidWind_'+str(i+1)+'.png')).write_bytes(base64.b64decode(cap['data']));print('FLUID_FRAME',i+1,flush=True)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 call('save_assets',{'asset_paths':[]},ASSET)
 call('set_properties',{'instance':ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),'values':json.dumps({'bThrottleCPUWhenNotForeground':True})},OBJ)
