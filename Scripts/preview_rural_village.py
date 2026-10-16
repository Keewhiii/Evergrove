from build_companion_combat import *
import time,math
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools'
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
T='/Game/Tests/World/BP_GuildMovementProbe.BP_GuildMovementProbe'
OUT=ROOT/'Saved/RuralVillageAudit';OUT.mkdir(exist_ok=True)
def find(name='',cls=None):
 a={'name':name,'tag':'','collision_channels':[]}
 if cls:a['actor_type']=ref(cls)
 return call('find_actors',a,SCENE)
def get(o,keys):return json.loads(call('get_properties',{'instance':o,'properties':keys},OBJ))
def props(o,values):return call('set_properties',{'instance':o,'values':json.dumps(values)},OBJ)
def move(pos):
 call('set_actor_transform',{'actor':player,'xform':{'location':dict(zip('xyz',pos))},'worldspace':True},ACT);time.sleep(.7)
def shot(name):
 props(live,{'ScreenshotCommand':'HighResShot 1600x900 filename="'+str(OUT/(name+'.png')).replace('\\','/')+'"','ScreenshotRequested':True});time.sleep(.4)
probe=call('add_to_scene_from_asset',{'asset_path':T.split('.')[0],'name':'Rural_TemporaryProbe','xform':{},'snap_to_ground':False},SCENE)
report={}
try:
 props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
 call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':0}},APP);time.sleep(.6)
 world=find(cls=W+'_C')[0];player=find(cls=PLAYER+'_C')[0];live=find('Rural_TemporaryProbe')[0]
 props(world,{'ClockPaused':True,'TimeOfDayMinutes':720})
 camera=get(world,['FollowCamera'])['FollowCamera'];component=call('get_components',{'actor':camera,'component_type':ref('/Script/Engine.CameraComponent')},ACT)[0]
 time.sleep(6)
 movement=call('get_components',{'actor':player,'component_type':ref('/Script/Engine.CharacterMovementComponent')},ACT)[0]
 original_speed=get(movement,['MaxWalkSpeed'])['MaxWalkSpeed'];props(movement,{'MaxWalkSpeed':120})
 # Follow the forest route using real movement input rather than teleporting between stops.
 move((3550,470,110));walked=[]
 for target in [(3550,260),(3200,100),(2900,-80),(2500,-40),(2200,140),(1850,110),(1500,-40),(1100,-70),(780,100)]:
  deadline=time.monotonic()+12
  while time.monotonic()<deadline:
   p=call('get_actor_transform',{'actor':player},ACT)['location'];dx=target[0]-p['x'];dy=target[1]-p['y'];distance=math.hypot(dx,dy)
   if distance<65:break
   props(live,{'Moving':True,'Direction':{'x':dx/distance,'y':dy/distance,'z':0}});time.sleep(.12)
  props(live,{'Moving':False});assert distance<65,{'blocked_at':p,'target':target}
  walked.append(p)
 report['walked_forest_route']=walked
 props(movement,{'MaxWalkSpeed':original_speed})
 move((-1500,0,110));props(component,{'OrthoWidth':5400});shot('Village_Overview');props(component,{'OrthoWidth':1200})
 for name,pos in [('Guild_Front',(-516,-530,110)),('Cottages',(-2310,280,110)),('Farms',(-1950,2400,110)),('Forest_Approach',(3250,350,110))]:move(pos);shot(name)
 move((-900,350,110));props(world,{'TimeOfDayMinutes':0});time.sleep(.4);shot('Village_Night')
 lamp=find('LocalGuild_WindowLight0')[0];light=call('get_components',{'actor':lamp,'component_type':ref('/Script/Engine.PointLightComponent')},ACT)[0]
 report['night_window']=get(light,['Intensity']);assert report['night_window']['Intensity']>300
 props(world,{'TimeOfDayMinutes':720});time.sleep(.2);report['day_window']=get(light,['Intensity']);assert report['day_window']['Intensity']==0
 # Walk-through portals are tested through their actual approach/animation timers.
 entrance=find('LocalGuild_Entrance')[0];position=call('get_actor_transform',{'actor':entrance},ACT)['location']
 move((position['x'],position['y']+65,110));time.sleep(.8)
 interior=call('get_actor_transform',{'actor':player},ACT)['location'];assert interior['y']<-5000,interior
 report['guild_entry']=interior;shot('Guild_Interior_Day')
 report['interior_day']=get(world,['Daylight','InteriorLightingActive']);assert report['interior_day']['InteriorLightingActive']
 props(world,{'TimeOfDayMinutes':0});time.sleep(.3);shot('Guild_Interior_Night');report['interior_night']=get(world,['InteriorLightingActive']);assert report['interior_night']['InteriorLightingActive']
 exit=find('LocalGuild_Exit')[0];position=call('get_actor_transform',{'actor':exit},ACT)['location']
 move((position['x'],position['y']-65,110));time.sleep(.8)
 exterior=call('get_actor_transform',{'actor':player},ACT)['location'];assert exterior['y']>-5000,exterior
 report['guild_exit']=exterior
 (OUT/'runtime.json').write_text(json.dumps(report,indent=2));print('RURAL_VILLAGE_PREVIEW_AND_PORTALS_PASSED '+json.dumps(report),flush=True)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 call('remove_from_scene',{'actor':probe},SCENE)
 props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':True})
