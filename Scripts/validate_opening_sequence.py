"""Exercise normal and skipped new-game cinematics without production saves."""
from build_companion_combat import *
import time
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools'
O='/Game/Game/UI/BP_EvergroveOpeningHUD.BP_EvergroveOpeningHUD'
M='/Game/Game/UI/BP_EvergroveIntroHUD.BP_EvergroveIntroHUD'
T='/Game/Tests/World/BP_IntroValidation.BP_IntroValidation'
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
OUT=ROOT/'Saved/OpeningSequenceAudit';OUT.mkdir(exist_ok=True)
def get(o,keys):return json.loads(call('get_properties',{'instance':o,'properties':keys},OBJ))
def props(o,values):return call('set_properties',{'instance':o,'values':json.dumps(values)},OBJ)
def find(cls):return call('find_actors',{'name':'','tag':'','collision_channels':[],'actor_type':ref(cls+'_C')},SCENE)
def active(instance):return get(instance,['ActiveOpening'])['ActiveOpening']
def shot(opening,name):
 props(opening,{'CaptureCommand':'HighResShot 1600x900 filename="'+str(OUT/(name+'.png')).replace('\\','/')+'"','CaptureRequested':True});time.sleep(.3)
probe=call('add_to_scene_from_asset',{'asset_path':T.split('.')[0],'name':'Opening_TemporaryProbe','xform':{},'snap_to_ground':False},SCENE)
report={}
try:
 props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
 for mode in ['normal','skip']:
  call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':0}},APP);time.sleep(.3)
  live=find(T)[0];props(live,{'Action':4,'Requested':True});time.sleep(.2)
  menu=get(live,['Menu'])['Menu'];instance=get(menu,['Instance'])['Instance']
  props(menu,{'HasSave':False,'Selected':0});props(live,{'Action':1,'Requested':True});time.sleep(.3)
  dream=active(instance);assert isinstance(dream,dict),dream
  assert get(dream,['Phase'])['Phase']==0
  props(dream,{'Age':1.6});time.sleep(.1)
  assert get(dream,['Caption'])['Caption']=='Oh, child of life...'
  if mode=='normal':
   shot(dream,'Dream_ChildOfLife')
   props(dream,{'Age':21.1});time.sleep(.1);shot(dream,'Dream_Worldline')
   props(dream,{'Age':29.6})
  else:props(dream,{'RequestedSkip':True})
  time.sleep(.8)
  wake=active(instance);assert get(wake,['Phase'])['Phase']==1,wake
  props(wake,{'Age':3.0});time.sleep(.2)
  world=find(W)[0]
  state=get(world,['DayNumber','TimeOfDayMinutes','ClockPaused','FollowCamera'])
  assert state['DayNumber']==1 and state['TimeOfDayMinutes']==480 and state['ClockPaused'],state
  player=find(PLAYER)[0]
  location=call('get_actor_transform',{'actor':player},ACT)['location']
  assert abs(location['x']-9200)<1 and abs(location['y']-1800)<1,location
  sprite=call('get_components',{'actor':player,'component_type':ref('/Script/Paper2D.PaperFlipbookComponent')},ACT)[0]
  pose=get(sprite,['RelativeRotation','RelativeLocation']);assert pose['RelativeRotation']['pitch']>85,pose
  hunter=call('find_actors',{'name':'Village_Rein','tag':'','collision_channels':[]},SCENE)[0]
  hunter_location=call('get_actor_transform',{'actor':hunter},ACT)['location']
  assert abs(hunter_location['x']-location['x'])<200 and abs(hunter_location['y']-location['y'])<200,hunter_location
  report[mode]={'wake':state,'spawn':location,'caption':get(wake,['Caption'])}
  if mode=='normal':
   shot(wake,'Awakening')
   props(wake,{'Age':23.0});time.sleep(.1);shot(wake,'Hunter_Directions')
   props(wake,{'Age':26.1})
  else:props(wake,{'RequestedSkip':True})
  time.sleep(.3)
  assert get(instance,['ActiveOpening'])['ActiveOpening']=='None'
  assert not get(world,['ClockPaused'])['ClockPaused']
  assert abs(get(sprite,['RelativeRotation'])['RelativeRotation']['pitch'])<.01
  camera=get(wake,['Camera']) if False else state['FollowCamera']
  report[mode]['finished_clock']=get(world,['TimeOfDayMinutes','ClockPaused'])
  call('StopPIE',{},APP)
 (OUT/'runtime.json').write_text(json.dumps(report,indent=2))
 print('OPENING_NORMAL_AND_SKIP_PASSED '+json.dumps(report),flush=True)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 call('remove_from_scene',{'actor':probe},SCENE)
 props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':True})
