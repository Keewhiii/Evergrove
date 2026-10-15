"""Test actual movement-triggered leaf bursts, cleanup, continuous sway and visible gusts."""
from build_companion_combat import call,ref,ROOT,OBJ,ASSET,SCENE,graph,var,create
import json,time,base64
ACT='editor_toolset.toolsets.actor.ActorTools';APP='EditorToolset.EditorAppToolset';MAT='editor_toolset.toolsets.material.MaterialTools';TEST='/Game/Tests/World/BP_GrassMovementProbe.BP_GrassMovementProbe';OUT=ROOT/'Saved/WoodlandWindFXAudit'
def props(o,p):return call('set_properties',{'instance':o,'values':json.dumps(p)},OBJ)
props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
probe=call('add_to_scene_from_asset',{'asset_path':TEST.split('.')[0],'name':'WindFX_TemporaryMovementProbe','xform':{'location':{'x':0,'y':0,'z':0}},'snap_to_ground':False},SCENE);call('set_label',{'actor':probe,'label':'WindFX_TemporaryMovementProbe'},ACT)
report={}
try:
 try:call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','startTransform':{'location':{'x':1550,'y':470,'z':100},'rotation':{'pitch':0,'yaw':180,'roll':0}},'warmupSeconds':0}},APP)
 except RuntimeError as e:
  if 'PIE ended before warmup completed' not in str(e):raise
 assert call('IsPIERunning',{},APP)
 start=time.monotonic()
 live=call('find_actors',{'name':'WindFX_TemporaryMovementProbe','tag':'','collision_channels':[]},SCENE)[0]
 player=call('find_actors',{'name':'','actor_type':ref('/Game/Game/Characters/Player/Blueprints/BP_Player.BP_Player_C'),'tag':'','collision_channels':[]},SCENE)[0]
 world=call('find_actors',{'name':'','actor_type':ref('/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld_C'),'tag':'','collision_channels':[]},SCENE)[0]
 move=call('get_components',{'actor':player,'component_type':ref('/Script/Engine.CharacterMovementComponent')},ACT)[0]
 def sample():return json.loads(call('get_properties',{'instance':world,'properties':['GrassMoveEnergy','GrassLeafBurstCount','GrassLeafCenters']},OBJ))
 def bursts():return call('find_actors',{'name':'','actor_type':ref('/Game/Game/World/BP_RunLeafBurst.BP_RunLeafBurst_C'),'tag':'','collision_channels':[]},SCENE)
 time.sleep(.4);idle=sample();assert idle['GrassLeafBurstCount']==0
 props(move,{'MaxWalkSpeed':200});props(live,{'Moving':True});time.sleep(.8);walk=sample();assert walk['GrassLeafBurstCount']==0
 props(move,{'MaxWalkSpeed':400});time.sleep(.8);run=sample();assert run['GrassLeafBurstCount']>0,run
 active=bursts();assert active
 for actor in active:
  for c in call('get_components',{'actor':actor,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT):
   p=json.loads(call('get_properties',{'instance':c,'properties':['BodyInstance','CustomPrimitiveData']},OBJ));assert p['BodyInstance']['collisionEnabled']=='NoCollision'
 cap=call('CaptureEditorImage',{},APP);(OUT/'RunLeafBurst.png').write_bytes(base64.b64decode(cap['data']))
 props(live,{'Moving':False});time.sleep(1.6);settled=sample();assert not bursts();time.sleep(.25);assert sample()['GrassLeafBurstCount']==settled['GrassLeafBurstCount']
 delay=7-(time.monotonic()-start)
 if delay>0:time.sleep(delay)
 cap=call('CaptureEditorImage',{},APP);(OUT/'VisibleGust.png').write_bytes(base64.b64decode(cap['data']))
 ribbons=call('find_actors',{'name':'Woodland_VisibleWind','tag':'','collision_channels':[]},SCENE);assert len(ribbons)==1
 xf=call('get_actor_transform',{'actor':player},ACT);xf['location']={'x':-900,'y':440,'z':100};call('set_actor_transform',{'actor':player,'xform':xf,'worldspace':True},ACT)
 before_bush=sample()['GrassLeafBurstCount'];props(live,{'Moving':True});time.sleep(.65);after_bush=sample()['GrassLeafBurstCount'];assert after_bush>before_bush
 props(live,{'Moving':False});time.sleep(1.5);assert not bursts()
 xf['location']={'x':1850,'y':0,'z':100};call('set_actor_transform',{'actor':player,'xform':xf,'worldspace':True},ACT)
 before_clear=sample()['GrassLeafBurstCount'];props(live,{'Moving':True});time.sleep(.65);after_clear=sample()['GrassLeafBurstCount'];assert after_clear==before_clear
 props(live,{'Moving':False})
 report={'idle_bursts':idle['GrassLeafBurstCount'],'walk_bursts':walk['GrassLeafBurstCount'],'run_bursts':run['GrassLeafBurstCount'],'bush_run_bursts':after_bush-before_bush,'clear_path_bursts':after_clear-before_clear,'live_bursts_running':len(active),'live_bursts_after_settling':0,'vegetation_centers':len(run['GrassLeafCenters']),'visible_wind_fields':len(ribbons)}
 print('WIND_AND_BURSTS_VERIFIED '+json.dumps(report),flush=True)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 call('remove_from_scene',{'actor':probe},SCENE);call('save_assets',{'asset_paths':[]},ASSET);props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':True})
(OUT/'runtime.json').write_text(json.dumps(report,indent=2))
