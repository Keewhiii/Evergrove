from build_companion_combat import *
_original_call=call
def call(name,args,toolset=None):
 try:return _original_call(name,args,toolset)
 except RuntimeError as exc:
  if name=='StartPIE' and 'PIE ended before warmup completed' in str(exc):
   import time
   time.sleep(1)
   if _original_call('IsPIERunning',{},'EditorToolset.EditorAppToolset'):return None
  raise

import time,math,sys
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools';W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld';T='/Game/Tests/World/BP_ForestTravelValidation.BP_ForestTravelValidation'
OUT=ROOT/'Saved/SeparateForestAudit';OUT.mkdir(exist_ok=True)
layout=json.loads((ROOT/'ContentSource/RuralVillage/forest_layout.json').read_text())
def find(n='',cls=None):
 a={'name':n,'tag':'','collision_channels':[]}
 if cls:a['actor_type']=ref(cls)
 return call('find_actors',a,SCENE)
def props(a,v):return call('set_properties',{'instance':a,'values':json.dumps(v)},OBJ)
def get(a,keys):return json.loads(call('get_properties',{'instance':a,'properties':keys},OBJ))
def loc(a):return call('get_actor_transform',{'actor':a},ACT)['location']
def move(x,y):call('set_actor_transform',{'actor':player,'xform':{'location':{'x':x,'y':y,'z':110}},'worldspace':True},ACT);time.sleep(.3)
def shot(gate,name):props(gate,{'CaptureCommand':'HighResShot 1600x900 filename="'+str(OUT/(name+'.png')).replace('\\','/')+'"','CaptureRequested':True});time.sleep(.25)
assert not find('Footpath') and not find('LocalGuild'),'Forest contains town/path actors'
probe=call('add_to_scene_from_asset',{'asset_path':T.split('.')[0],'name':'SeparateForest_TemporaryProbe','xform':{},'snap_to_ground':False},SCENE)
report={}
try:
 props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
 call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':0}},APP);time.sleep(.5)
 player=find(cls=PLAYER+'_C')[0];world=find(cls=W+'_C')[0];live=find('SeparateForest_TemporaryProbe')[0];gate=find('Forest_ExitToVillage')[0]
 props(world,{'ClockPaused':True,'TimeOfDayMinutes':720});time.sleep(.15);shot(gate,'Forest_WakingClearing')
 camera=get(world,['FollowCamera'])['FollowCamera'];cam=call('get_components',{'actor':camera,'component_type':ref('/Script/Engine.CameraComponent')},ACT)[0]
 move(6700,-600);props(cam,{'OrthoWidth':11000});shot(gate,'Forest_Overview');props(cam,{'OrthoWidth':1200});move(9200,1800)
 movement=call('get_components',{'actor':player,'component_type':ref('/Script/Engine.CharacterMovementComponent')},ACT)[0];speed=get(movement,['MaxWalkSpeed'])['MaxWalkSpeed'];props(movement,{'MaxWalkSpeed':260})
 walked=[]
 for target in ([] if '--travel-only' in sys.argv else layout['route'][1:-1]+[layout['return_arrival']]):
  deadline=time.monotonic()+14
  while time.monotonic()<deadline:
   p=loc(player);dx=target[0]-p['x'];dy=target[1]-p['y'];distance=math.hypot(dx,dy)
   if distance<100:break
   props(live,{'Moving':True,'Direction':{'x':dx/distance,'y':dy/distance,'z':0}});time.sleep(.08)
  props(live,{'Moving':False});assert distance<100,{'blocked':p,'target':target};walked.append(p)
 props(movement,{'MaxWalkSpeed':speed});report['walked_route']=walked;move(*layout['return_arrival']);shot(gate,'Forest_ExitGate')
 move(8500,1900);props(cam,{'OrthoWidth':2400});shot(gate,'Forest_Lake');props(cam,{'OrthoWidth':1200})
 move(4500,2250);shot(gate,'Forest_Pond_A');move(7550,-4425);shot(gate,'Forest_Pond_B')
 river_x=5750+180*math.sin(-3150/1200)+90*math.sin(-3150/470);move(river_x,-3150);props(cam,{'OrthoWidth':1800});shot(gate,'Forest_CreekBridge');props(cam,{'OrthoWidth':1200})
 props(world,{'DayNumber':13,'TimeOfDayMinutes':1031.23456789,'ClockPaused':True});props(live,{'GoldValue':137,'Requested':True});time.sleep(1)
 assert get(player,['Gold'])['Gold']==137, get(player,['Gold'])
 move(layout['exit'][0]+100,layout['exit'][1])
 deadline=time.monotonic()+12
 while time.monotonic()<deadline:
  ps=find(cls=PLAYER+'_C');ws=find(cls=W+'_C')
  if ps and ws and 'L_EvergroveStart' in ws[0]['refPath'] and get(ws[0],['DayNumber'])['DayNumber']==13:break
  time.sleep(.1)
 player=find(cls=PLAYER+'_C')[0];world=find(cls=W+'_C')[0]
 assert 'L_EvergroveStart' in world['refPath'],world
 p=loc(player);assert abs(p['x']-3200)<1 and abs(p['y'])<1,p
 clock=get(world,['DayNumber','TimeOfDayMinutes','ClockPaused']);assert clock['DayNumber']==13 and clock['TimeOfDayMinutes']==1031.23456789 and clock['ClockPaused'],clock
 assert get(player,['Gold'])['Gold']==137
 report['town_arrival']={'position':p,'clock':clock,'gold':137}
 gate=find('Village_ReturnToForest')[0];time.sleep(.5);shot(gate,'Town_Approach')
 move(3500,0)
 deadline=time.monotonic()+12
 while time.monotonic()<deadline:
  ps=find(cls=PLAYER+'_C');ws=find(cls=W+'_C')
  if ps and ws and 'L_EvergroveForest' in ws[0]['refPath'] and get(ws[0],['DayNumber'])['DayNumber']==13:break
  time.sleep(.1)
 player=find(cls=PLAYER+'_C')[0];world=find(cls=W+'_C')[0];assert 'L_EvergroveForest' in world['refPath'],world
 p=loc(player);assert abs(p['x']-layout['return_arrival'][0])<1 and abs(p['y']-layout['return_arrival'][1])<1,p
 assert get(world,['TimeOfDayMinutes'])['TimeOfDayMinutes']==1031.23456789
 report['return_to_forest']=p
 (OUT/'runtime.json').write_text(json.dumps(report,indent=2));print('SEPARATE_FOREST_GRASS_ROUTE_BRIDGE_AND_BIDIRECTIONAL_TRAVEL_PASSED',flush=True)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 call('remove_from_scene',{'actor':probe},SCENE)
 props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':True})
