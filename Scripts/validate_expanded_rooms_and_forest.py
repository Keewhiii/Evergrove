from build_companion_combat import *
import math,time,sys
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools'
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld';T='/Game/Tests/World/BP_GuildMovementProbe.BP_GuildMovementProbe'
layout=json.loads((ROOT/'ContentSource/RuralVillage/layout.json').read_text())
OUT=ROOT/'Saved/ExpandedRoomsAudit';OUT.mkdir(exist_ok=True)
def find(name='',cls=None):
 a={'name':name,'tag':'','collision_channels':[]}
 if cls:a['actor_type']=ref(cls)
 return call('find_actors',a,SCENE)
def get(a,keys):return json.loads(call('get_properties',{'instance':a,'properties':keys},OBJ))
def props(a,v):return call('set_properties',{'instance':a,'values':json.dumps(v)},OBJ)
def location(a):return call('get_actor_transform',{'actor':a},ACT)['location']
def move(x,y,z=110):call('set_actor_transform',{'actor':player,'xform':{'location':{'x':x,'y':y,'z':z}},'worldspace':True},ACT);time.sleep(.35)
def shot(name):props(live,{'ScreenshotCommand':'HighResShot 1600x900 filename="'+str(OUT/(name+'.png')).replace('\\','/')+'"','ScreenshotRequested':True});time.sleep(.25)
rooms=layout['interiors']
for r in rooms:
 assert r['size'][0]>=2200 and r['size'][1]>=1800,r
 for other in rooms:
  if r is other:continue
  assert math.dist(r['center'],other['center'])>=12000,(r,other)
probe=call('add_to_scene_from_asset',{'asset_path':T.split('.')[0],'name':'ExpandedRooms_TemporaryProbe','xform':{},'snap_to_ground':False},SCENE)
report={'isolated_rooms':len(rooms),'minimum_room_distance':12000,'interiors':{}}
try:
 props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
 call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':0}},APP)
 time.sleep(.8);player=find(cls=PLAYER+'_C')[0];live=find('ExpandedRooms_TemporaryProbe')[0];world=find(cls=W+'_C')[0]
 props(world,{'ClockPaused':True,'TimeOfDayMinutes':720})
 camera=get(world,['FollowCamera'])['FollowCamera'];component=call('get_components',{'actor':camera,'component_type':ref('/Script/Engine.CameraComponent')},ACT)[0]
 movement=call('get_components',{'actor':player,'component_type':ref('/Script/Engine.CharacterMovementComponent')},ACT)[0]
 speed=get(movement,['MaxWalkSpeed'])['MaxWalkSpeed'];props(movement,{'MaxWalkSpeed':260})
 move(9200,1800);shot('Forest_Clearing');walked=[]
 for target in ([] if '--rooms-only' in sys.argv else layout['trail'][1:-1]):
  deadline=time.monotonic()+14
  while time.monotonic()<deadline:
   p=location(player);dx=target[0]-p['x'];dy=target[1]-p['y'];distance=math.hypot(dx,dy)
   if distance<105:break
   props(live,{'Moving':True,'Direction':{'x':dx/distance,'y':dy/distance,'z':0}});time.sleep(.08)
  props(live,{'Moving':False});assert distance<105,{'blocked_at':p,'target':target};walked.append(p)
 props(movement,{'MaxWalkSpeed':speed});report['forest_escape_route']=walked;shot('Forest_Exit')
 for name in ['MaraCottage','TobinCottage','NellCottage','LocalGuild','FarmBarn']:
  entrance=find(name+'_Entrance')[0];p=location(entrance);move(p['x'],p['y']+65);time.sleep(.6)
  r=next(r for r in rooms if r['building']==name);p=location(player)
  assert abs(p['x']-r['center'][0])<100 and abs(p['y']-r['center'][1])<r['size'][1]/2,p
  state=get(world,['InteriorLightingActive','Daylight']);assert state['InteriorLightingActive'],state
  move(r['center'][0],r['center'][1]+100);props(component,{'OrthoWidth':2700});shot(name+'_Interior')
  sun=get(world,['ClockSun'])['ClockSun'];sunlight=call('get_components',{'actor':sun,'component_type':ref('/Script/Engine.LightComponent')},ACT)[0]
  day_light=get(sunlight,['Intensity','LightColor'])
  props(world,{'TimeOfDayMinutes':0});time.sleep(.3);night=get(world,['InteriorLightingActive','Daylight']);assert night['InteriorLightingActive'],night
  assert get(sunlight,['Intensity','LightColor'])==day_light,night
  report['interiors'][name]={'entry':p,'size':r['size'],'night':night}
  props(world,{'TimeOfDayMinutes':720});props(component,{'OrthoWidth':1200})
  exit=find(name+'_Exit')[0];p=location(exit);move(p['x'],p['y']-65);time.sleep(.6);assert location(player)['y']>-5000
 (OUT/'runtime.json').write_text(json.dumps(report,indent=2));print('LARGE_ROOMS_ISOLATION_FOREST_ESCAPE_AND_LIGHTING_PASSED',flush=True)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 call('remove_from_scene',{'actor':probe},SCENE)
 props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':True})
