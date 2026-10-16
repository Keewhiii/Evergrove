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


import time
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools'
OUT=ROOT/'Saved/WaterAdjustmentAudit'
T='/Game/Tests/World/BP_ForestTravelValidation'
probe=call('add_to_scene_from_asset',{'asset_path':T,'name':'WaterContact_TemporaryProbe','xform':{},'snap_to_ground':False},SCENE)
def find(n='',cls=None):
 a={'name':n,'tag':'','collision_channels':[]}
 if cls:a['actor_type']=ref(cls)
 return call('find_actors',a,SCENE)[0]
def props(a,v):call('set_properties',{'instance':a,'values':json.dumps(v)},OBJ)
def sample(label):
 props(gate,{'CaptureCommand':'py "E:/UE5 Projects/AdventureRPG/Scripts/capture_water_contact_runtime.py"','CaptureRequested':True});time.sleep(.35)
 result=json.loads((OUT/'contact_sample.json').read_text())
 props(gate,{'CaptureCommand':'HighResShot 1600x900 filename="'+str(OUT/(label+'.png')).replace('\\','/')+'"','CaptureRequested':True});time.sleep(.3)
 return result
try:
 call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':0}},APP)
 time.sleep(.6)
 player=find(cls=PLAYER+'_C');world=find(cls='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld_C');gate=find('Forest_ExitToVillage');live=find('WaterContact_TemporaryProbe')
 props(world,{'ClockPaused':True,'TimeOfDayMinutes':720})
 call('set_actor_transform',{'actor':player,'xform':{'location':{'x':8500,'y':2070,'z':110}},'worldspace':True},ACT)
 time.sleep(.4)
 results={'idle':sample('ContactIdle')}
 props(live,{'Moving':True,'Direction':{'x':1,'y':0,'z':0}});time.sleep(.3)
 results['moving']=sample('ContactMoving')
 props(live,{'Moving':False});time.sleep(.8)
 results['stopped']=sample('ContactStopped')
 assert results['idle']['activity']==0,results
 assert results['moving']['activity']>.1,results
 assert results['stopped']['activity']==0,results
 (OUT/'contact_runtime.json').write_text(json.dumps(results,indent=2));print('WATER_CONTACT_IDLE_MOVING_STOPPED_PASSED',results)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 call('remove_from_scene',{'actor':probe},SCENE)
