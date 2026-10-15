"""Exercise real CharacterMovement through grass, then verify that the response settles."""
from build_companion_combat import call,ref,ROOT,OBJ,ASSET,SCENE,graph,var,create
import json,time,base64
ACT='editor_toolset.toolsets.actor.ActorTools';APP='EditorToolset.EditorAppToolset';TEST='/Game/Tests/World/BP_GrassMovementProbe.BP_GrassMovementProbe';OUT=ROOT/'Saved/BroadleafGrassAudit'
def props(o,p):return call('set_properties',{'instance':o,'values':json.dumps(p)},OBJ)
props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
create(TEST,'/Script/Engine.Actor');var(TEST,'Moving','bool')
call('set_variable_instance_editable',{'blueprint':ref(TEST),'variable_name':'Moving','instance_editable':True})
graph(TEST,'EventGraph','''(event EventTick (DeltaSeconds)
 (if (Variables|Default|GetMoving)
  (Pawn|Input|AddMovementInput :self (Game|GetPlayerCharacter 0) :WorldDirection (Math|Vector|MakeVector 1.0 0.0 0.0) :ScaleValue 1.0)))''')
probe=call('add_to_scene_from_asset',{'asset_path':TEST.split('.')[0],'name':'Grass_TemporaryMovementProbe','xform':{'location':{'x':0,'y':0,'z':0}},'snap_to_ground':False},SCENE)
call('set_label',{'actor':probe,'label':'Grass_TemporaryMovementProbe'},ACT)
report={}
try:
 try:call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','startTransform':{'location':{'x':1550,'y':470,'z':100},'rotation':{'pitch':0,'yaw':180,'roll':0}},'warmupSeconds':0}},APP)
 except RuntimeError as e:
  if 'PIE ended before warmup completed' not in str(e):raise
 assert call('IsPIERunning',{},APP)
 live=call('find_actors',{'name':'Grass_TemporaryMovementProbe','tag':'','collision_channels':[]},SCENE)[0]
 player=call('find_actors',{'name':'','actor_type':ref('/Game/Game/Characters/Player/Blueprints/BP_Player.BP_Player_C'),'tag':'','collision_channels':[]},SCENE)[0]
 world=call('find_actors',{'name':'','actor_type':ref('/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld_C'),'tag':'','collision_channels':[]},SCENE)[0]
 move=call('get_components',{'actor':player,'component_type':ref('/Script/Engine.CharacterMovementComponent')},ACT)[0]
 def sample():return json.loads(call('get_properties',{'instance':world,'properties':['GrassMoveEnergy']},OBJ))['GrassMoveEnergy']
 time.sleep(.5);report['idle']=sample();assert report['idle']<.02
 props(move,{'MaxWalkSpeed':200});props(live,{'Moving':True});time.sleep(.8);report['walk']=sample();assert report['walk']>.2,report
 props(move,{'MaxWalkSpeed':400});time.sleep(.8);report['run']=sample();assert report['run']>report['walk']*1.4,report
 cap=call('CaptureEditorImage',{},APP);(OUT/'Grass_RunInteraction.png').write_bytes(base64.b64decode(cap['data']))
 props(live,{'Moving':False});time.sleep(1.2);report['settled']=sample();assert report['settled']<.03,report
 report['final_player_transform']=call('get_actor_transform',{'actor':player},ACT)
 cap=call('CaptureEditorImage',{},APP);(OUT/'Grass_TreePalette.png').write_bytes(base64.b64decode(cap['data']))
 print('GRASS_MOVEMENT_VERIFIED '+json.dumps(report),flush=True)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 call('remove_from_scene',{'actor':probe},SCENE)
 call('save_assets',{'asset_paths':[]},ASSET)
 props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':True})
(OUT/'player_interaction_runtime.json').write_text(json.dumps(report,indent=2))
