"""Update runtime decoration and inspect the grass patches in actual Play mode."""
from build_companion_combat import call,ref,ROOT,OBJ,ASSET,SCENE,graph
import json,time,base64
COZY='/Game/Game/World/BP_CozyWoodland.BP_CozyWoodland';ACT='editor_toolset.toolsets.actor.ActorTools';APP='EditorToolset.EditorAppToolset';OUT=ROOT/'Saved/BroadleafGrassAudit'
for name in ['Dress2','Dress3']:
 source=(ROOT/'Saved/CombatAudit'/(name+'.dsl')).read_text(encoding='utf-8')
 source=source.replace('/Game/Environment/PixelProps/SM_Prop_Grass.SM_Prop_Grass','/Game/Environment/BroadleafGrass/SM_BroadleafGrass.SM_BroadleafGrass').replace('/Game/Environment/PixelProps/M_Prop_Grass.M_Prop_Grass','/Game/Environment/BroadleafGrass/M_BroadleafGrass.M_BroadleafGrass')
 graph(COZY,name,source)
call('save_assets',{'asset_paths':[]},ASSET)
try:
 try:call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','startTransform':{'location':{'x':1850,'y':140,'z':100},'rotation':{'pitch':0,'yaw':180,'roll':0}},'warmupSeconds':0}},APP)
 except RuntimeError as e:
  if 'PIE ended before warmup completed' not in str(e):raise
 assert call('IsPIERunning',{},APP)
 time.sleep(3)
 cozy=call('find_actors',{'name':'BP_CozyWoodland','tag':'','collision_channels':[]},SCENE);count=0
 for actor in cozy:
  for c in call('get_components',{'actor':actor,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT):
   p=json.loads(call('get_properties',{'instance':c,'properties':['StaticMesh','BodyInstance']},OBJ))
   if 'SM_BroadleafGrass' in p['StaticMesh']['refPath']:
    assert p['BodyInstance']['collisionEnabled']=='NoCollision';count+=1
   assert 'SM_Prop_Grass' not in p['StaticMesh']['refPath']
 assert count==10,count
 camera=call('find_actors',{'name':'Woodland_FollowCamera','tag':'','collision_channels':[]},SCENE)[0]
 xf=call('get_actor_transform',{'actor':camera},ACT);assert abs(xf['rotation']['pitch']+31)<.01
 cap=call('CaptureEditorImage',{},APP);(OUT/'Grass_PlayMode.png').write_bytes(base64.b64decode(cap['data']))
 (OUT/'runtime.json').write_text(json.dumps({'runtime_grass_tiles':count,'camera_pitch':xf['rotation']['pitch'],'collision_errors':[]},indent=2));print('BROADLEAF_RUNTIME_VERIFIED',count,flush=True)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 call('save_assets',{'asset_paths':[]},ASSET)
 call('set_properties',{'instance':ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),'values':json.dumps({'bThrottleCPUWhenNotForeground':True})},OBJ)
