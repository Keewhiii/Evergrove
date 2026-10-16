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


import time,math
from forest_terrain_height import terrain_height
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools';OUT=ROOT/'Saved/ForestAtmosphereAudit';OUT.mkdir(exist_ok=True)
def find(name='',tag='',cls=None):
 a={'name':name,'tag':tag,'collision_channels':[]}
 if cls:a['actor_type']=ref(cls)
 return call('find_actors',a,SCENE)
def props(a,v):call('set_properties',{'instance':a,'values':json.dumps(v)},OBJ)
def xf(a):return call('get_actor_transform',{'actor':a},ACT)
def shot(name):
 props(gate,{'CaptureCommand':'HighResShot 1600x900 filename="'+str(OUT/(name+'.png')).replace('\\','/')+'"','CaptureRequested':True});time.sleep(.4)
try:
 props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
 call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':0}},APP);time.sleep(.5)
 player=find(cls=PLAYER+'_C')[0];world=find(cls='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld_C')[0];gate=find('Forest_ExitToVillage')[0]
 props(world,{'ClockPaused':True,'TimeOfDayMinutes':720})
 effects=find(tag='ForestAtmosphere');assert len(effects)==26,len(effects)
 before={a['refPath']:xf(a) for a in effects};samples=[]
 for label,x,y in [('Canopy',9200,1800),('West',2600,600),('North',6700,-5400),('East',10000,4000),('Logs',7300,1800),('Slope',8450,-1425)]:
  call('set_actor_transform',{'actor':player,'xform':{'location':{'x':x,'y':y,'z':110+terrain_height(x,y)}},'worldspace':True},ACT);time.sleep(1.2)
  for a in effects:
   assert xf(a)==before[a['refPath']],a
   assert not json.loads(call('get_properties',{'instance':a,'properties':['bHidden']},OBJ))['bHidden'],a
  samples.append({'location':xf(player)['location'],'label':label});shot(label)
  if label in ['Canopy','Logs']:time.sleep(2);shot(label+'Later')
 (OUT/'runtime.json').write_text(json.dumps({'stationary_effects':len(effects),'samples':samples},indent=2));print('FOREST_WIDE_WORLD_ANCHORED_ATMOSPHERE_PASSED')
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':True})
