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
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools';OUT=ROOT/'Saved/ForestSpawnAudit';OUT.mkdir(exist_ok=True)
call('load_level',{'level_path':'/Game/Maps/L_EvergroveIntro'},SCENE)
call('load_level',{'level_path':'/Game/Maps/L_EvergroveForest'},SCENE)
start=call('find_actors',{'name':'','tag':'','collision_channels':[],'actor_type':ref('/Script/Engine.PlayerStart')},SCENE)[0]
saved=call('get_actor_transform',{'actor':start},ACT)['location'];assert saved['x']==9200 and saved['y']==1800,saved
try:
 call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':0}},APP);time.sleep(1)
 player=call('find_actors',{'name':'','tag':'','collision_channels':[],'actor_type':ref(PLAYER+'_C')},SCENE)[0]
 actual=call('get_actor_transform',{'actor':player},ACT)['location'];assert abs(actual['x']-9200)<10 and abs(actual['y']-1800)<10,actual
 gate=call('find_actors',{'name':'Forest_ExitToVillage','tag':'','collision_channels':[]},SCENE)[0]
 call('set_properties',{'instance':gate,'values':json.dumps({'CaptureCommand':'HighResShot 1600x900 filename="'+str(OUT/'ViewportSpawn.png').replace('\\','/')+'"','CaptureRequested':True})},OBJ);time.sleep(.5)
 (OUT/'runtime.json').write_text(json.dumps({'saved_player_start':saved,'default_viewport_spawn':actual},indent=2));print('DEFAULT_VIEWPORT_FOREST_SPAWN_PASSED',actual)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
