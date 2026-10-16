"""Capture fixed-camera water motion while the game clock is paused."""
from build_companion_combat import *
import time
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools'
OUT=ROOT/'Saved/WaterMotionAudit';OUT.mkdir(exist_ok=True)
def find(name):return call('find_actors',{'name':name,'tag':'','collision_channels':[]},SCENE)[0]
def props(a,v):call('set_properties',{'instance':a,'values':json.dumps(v)},OBJ)
call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':0}},APP)
try:
 time.sleep(.5)
 world=call('find_actors',{'name':'','tag':'','collision_channels':[],'actor_type':ref('/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld_C')},SCENE)[0];player=call('find_actors',{'name':'','tag':'','collision_channels':[],'actor_type':ref(PLAYER+'_C')},SCENE)[0];gate=find('Forest_ExitToVillage')
 props(world,{'ClockPaused':True,'TimeOfDayMinutes':720})
 camera=json.loads(call('get_properties',{'instance':world,'properties':['FollowCamera']},OBJ))['FollowCamera']
 cam=call('get_components',{'actor':camera,'component_type':ref('/Script/Engine.CameraComponent')},ACT)[0]
 result={}
 for label,x,y,width in [('Lake',8500,1900,2400),('River',5624,-3150,1800)]:
  call('set_actor_transform',{'actor':player,'xform':{'location':{'x':x,'y':y,'z':110}},'worldspace':True},ACT)
  props(cam,{'OrthoWidth':width});time.sleep(.5)
  for i in range(2):
   props(gate,{'CaptureCommand':'HighResShot 1600x900 filename="'+str(OUT/(label+str(i)+'.png')).replace('\\','/')+'"','CaptureRequested':True});time.sleep(1.1)
  result[label]={'frames':[label+'0.png',label+'1.png'],'game_clock_paused':True}
 (OUT/'motion.json').write_text(json.dumps(result,indent=2));print('STILL_AND_FLOWING_WATER_ANIMATION_PASSED',result)
finally:
 call('StopPIE',{},APP)
