"""Exercise automatic portals and real CharacterMovement up both staircases."""
from build_companion_combat import call,ref,ROOT,OBJ,ASSET,SCENE,graph,var,create
from woodland_fx_graph import props
import json,time,base64
ACT='editor_toolset.toolsets.actor.ActorTools';APP='EditorToolset.EditorAppToolset';OUT=ROOT/'Saved/GuildInteriorAudit';TEST='/Game/Tests/World/BP_GuildMovementProbe.BP_GuildMovementProbe'
LAYOUT=json.loads((ROOT/'ContentSource/GuildInterior/room_layout.json').read_text());RECEPTION_Y=-6000-LAYOUT['reception_approach_y_m']*100
create(TEST,'/Script/Engine.Actor')
for name,typ in [('Moving','bool'),('Direction','Vector'),('ScreenshotRequested','bool'),('ScreenshotCommand','string'),('InteractRequested','bool'),('DialogueCount','int')]:
 var(TEST,name,typ);call('set_variable_instance_editable',{'blueprint':ref(TEST),'variable_name':name,'instance_editable':True})
graph(TEST,'EventGraph','''(event EventTick (DeltaSeconds)
 (if (Variables|Default|GetMoving) (Pawn|Input|AddMovementInput :self (Game|GetPlayerCharacter 0) :WorldDirection (Variables|Default|GetDirection) :ScaleValue 1.0))
 (if (Variables|Default|GetScreenshotRequested)
  (Variables|Default|SetScreenshotRequested false)
  (Development|ExecuteConsoleCommand :Command (Variables|Default|GetScreenshotCommand) :SpecificPlayer (Game|GetPlayerController 0)))
 (if (Variables|Default|GetInteractRequested)
  (Variables|Default|SetInteractRequested false)
  (bind player (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0))
   (:then
    (Class|BPPlayer|SetInteractionDirection :self player :InteractionDirection (Math|Vector|MakeVector 0.0 -1.0 0.0))
    (Class|BPPlayer|PerformInteractionTrace :self player)) (:CastFailed)))
 (bind widgets (Widget|GetAllWidgetsOfClass :WidgetClass "/Game/Game/Characters/NPCs/WBP_Dialogue.WBP_Dialogue_C"))
 (Variables|Default|SetDialogueCount (Utilities|Array|Length widgets)))''')
probe=call('add_to_scene_from_asset',{'asset_path':TEST.split('.')[0],'name':'Guild_TemporaryProbe','xform':{},'snap_to_ground':False},SCENE);call('set_label',{'actor':probe,'label':'Guild_TemporaryProbe'},ACT)
report={}
def find(name='',cls=None):
 a={'name':name,'tag':'','collision_channels':[]}
 if cls:a['actor_type']=ref(cls)
 return call('find_actors',a,SCENE)
def get(o,keys):return json.loads(call('get_properties',{'instance':o,'properties':keys},OBJ))
def capture(name):
 c=call('CaptureEditorImage',{},APP);(OUT/(name+'.png')).write_bytes(base64.b64decode(c['data']))
def game_capture(name):
 props(live,{'ScreenshotCommand':'HighResShot 1400x900 filename="'+str(OUT/(name+'.png')).replace('\\','/')+'"','ScreenshotRequested':True});time.sleep(.5)
try:
 try:call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','startTransform':{'location':{'x':0,'y':-220,'z':100},'rotation':{'pitch':0,'yaw':180,'roll':0}},'warmupSeconds':0}},APP)
 except RuntimeError as e:
  if 'PIE ended before warmup completed' not in str(e):raise
 assert call('IsPIERunning',{},APP)
 player=find(cls='/Game/Game/Characters/Player/Blueprints/BP_Player.BP_Player_C')[0];live=find('Guild_TemporaryProbe')[0];entrance=find('GuildDoor_Entrance')[0];exit=find('GuildDoor_Exit')[0]
 move=call('get_components',{'actor':player,'component_type':ref('/Script/Engine.CharacterMovementComponent')},ACT)[0]
 def loc():return call('get_actor_transform',{'actor':player},ACT)['location']
 def teleport(x,y,z=100):
  xf=call('get_actor_transform',{'actor':player},ACT);xf['location']={'x':x,'y':y,'z':z};call('set_actor_transform',{'actor':player,'xform':xf,'worldspace':True},ACT)
 props(move,{'MaxWalkSpeed':300});teleport(0,-80);time.sleep(.7);capture('GroundAndEntrance');game_capture('GroundAndClosedDoorGame')
 left=find('GuildExterior_DoorLeft')[0];right=find('GuildExterior_DoorRight')[0]
 report['closed_leaf_yaws']=[call('get_actor_transform',{'actor':a},ACT)['rotation']['yaw'] for a in [left,right]]
 assert all(abs(y)<3 for y in report['closed_leaf_yaws']),report
 teleport(0,-300);time.sleep(.75)
 approach=get(entrance,['Opening','TransitionCount','Transitioning']);report['approach_opens_without_entering']=approach
 assert approach['Opening']>.9 and approach['TransitionCount']==0 and loc()['y']>-1000,report
 report['open_leaf_yaws']=[call('get_actor_transform',{'actor':a},ACT)['rotation']['yaw'] for a in [left,right]]
 assert report['open_leaf_yaws'][0]>70 and report['open_leaf_yaws'][1]<-70,report
 game_capture('DoorApproachedGame')
 teleport(0,-80);time.sleep(.7);assert get(entrance,['Opening'])['Opening']<.05
 teleport(0,-220)
 props(live,{'Direction':{'x':0,'y':-1,'z':0},'Moving':True})
 opening=None
 for _ in range(15):
  time.sleep(.1);opening=get(entrance,['Opening','Transitioning'])
  if opening['Opening']>.25 and opening['Transitioning']:break
 report['door_opening']=opening;assert opening['Opening']>.25,report
 game_capture('DoorOpeningGame')
 time.sleep(1.0);props(live,{'Moving':False});time.sleep(.2);report['entry_location']=loc();assert loc()['y']<-6000,report
 report['entry_portal']=get(entrance,['TransitionCount','Transitioning','LeftLeaf','RightLeaf']);assert report['entry_portal']['TransitionCount']==1
 report['interior_exit_leaves']=get(exit,['LeftLeaf','RightLeaf']);assert all(v in [None,'','None'] or (isinstance(v,dict) and not v.get('refPath')) for v in report['interior_exit_leaves'].values())
 capture('InteriorEntry')
 # Center reception remains within the existing 200cm interaction sphere trace.
 teleport(0,RECEPTION_Y);time.sleep(.4);capture('ReceptionGameplay')
 game_capture('ReceptionGame')
 luna=find('Woodland_Luna')[0];report['receptionist']=get(luna,['NPCName','QuestNPCID','HasChoices']);report['receptionist_location']=call('get_actor_transform',{'actor':luna},ACT)['location']
 # Ascend from the lowest step to the shared upper gallery using real movement.
 report['stairs']={}
 for side in [-1,1]:
  teleport(side*LAYOUT['stairs_x_m']*100,-6800);props(live,{'Direction':{'x':0,'y':-1,'z':0},'Moving':True});time.sleep(4.45);props(live,{'Moving':False});time.sleep(.15)
  p=loc();report['stairs'][str(side)]=p;assert p['z']>430 and p['y']<-8050,report
 capture('SecondFloorGameplay')
 game_capture('SecondFloorGame')
 # Exit from the room side, then verify no automatic bounce back.
 teleport(0,-6220);props(live,{'Direction':{'x':0,'y':1,'z':0},'Moving':True});time.sleep(1.8);props(live,{'Moving':False});time.sleep(.2)
 report['exit_location']=loc();report['exit_portal']=get(exit,['TransitionCount','Transitioning']);assert loc()['y']>-1000 and report['exit_portal']['TransitionCount']==1,report
 time.sleep(1.5);assert loc()['y']>-1000
 # Independent entry gates should only accept the door aperture, not nearby walls.
 teleport(230,-430);time.sleep(1.4);assert get(entrance,['TransitionCount'])['TransitionCount']==1
 report['side_wall_does_not_trigger']=True
 report['movement_input_restored']=get(move,['Velocity'])
 # Sprint around the actual tables/benches, using clear front, side and gallery routes.
 report['sprint_routes']={};props(move,{'MaxWalkSpeed':600})
 for name,start,direction,seconds,min_distance in [
  ('FrontCrossing',(-800,-6450,100),(1,0,0),2.55,1400),
  ('CentralAisle',(0,-6340,100),(0,-1,0),1.55,830),
  ('WestAisle',(-850,-6500,100),(0,-1,0),1.75,930),
  ('EastAisle',(850,-6500,100),(0,-1,0),1.75,930),
  ('BehindReception',(-500,-7960,100),(1,0,0),1.66,880),
  ('GalleryCrossing',(-600,-8120,460),(1,0,0),2.0,1080)]:
  teleport(*start);time.sleep(.15);begin=loc();props(live,{'Direction':dict(zip('xyz',direction)),'Moving':True});time.sleep(seconds);props(live,{'Moving':False});time.sleep(.15);end=loc()
  distance=sum((end[k]-begin[k])*v for k,v in zip('xyz',direction));report['sprint_routes'][name]={'start':begin,'end':end,'distance_cm':distance}
  assert distance>min_distance,report['sprint_routes']
 report['npc_spawn_markers']=len(call('find_actors',{'name':'','tag':'GuildNPCSpawn','collision_channels':[]},SCENE));assert report['npc_spawn_markers']==8
 teleport(0,-7000);time.sleep(.3);game_capture('RoomyHallGame')
 # Interact using the player's actual sphere trace, across the central counter.
 teleport(0,RECEPTION_Y);props(live,{'InteractRequested':True});time.sleep(.5)
 report['reception_dialogue_count']=get(live,['DialogueCount'])['DialogueCount'];report['reception_can_interact_after']=get(luna,['CanInteract'])
 assert report['reception_dialogue_count']==1,report
 capture('ReceptionDialogue');game_capture('ReceptionDialogueGame')
 print('GUILD_RUNTIME_VERIFIED',json.dumps(report),flush=True)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 call('remove_from_scene',{'actor':probe},SCENE);call('save_assets',{'asset_paths':[]},ASSET)
(OUT/'runtime.json').write_text(json.dumps(report,indent=2))
