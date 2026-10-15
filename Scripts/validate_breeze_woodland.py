"""Check the imported visual assets and capture calm/gust states in actual Play mode."""
from build_companion_combat import call,ref,ROOT,OBJ,ASSET,SCENE
import json,base64,time,math
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools';MAT='editor_toolset.toolsets.material.MaterialTools';OUT=ROOT/'Saved/BreezeWoodlandAudit';OUT.mkdir(exist_ok=True)
report={'gust_period':32,'states':[]}
for t in [0,6,20,38,52]:
 strength=max(0,min(1,(math.sin(math.tau*t/32)-.35)/.65));report['states'].append({'time':t,'gust':strength})
assert report['states'][0]['gust']==0 and report['states'][1]['gust']>.8 and report['states'][2]['gust']==0
materials=['/Game/Environment/LayeredWoodland/M_StackedLeaf_'+str(i)+'.M_StackedLeaf_'+str(i) for i in range(5)]+['/Game/Environment/PixelProps/M_Prop_Grass.M_Prop_Grass','/Game/Environment/LayeredWoodland/M_LayeredFlowerPixels.M_LayeredFlowerPixels','/Game/Environment/BreezeWoodland/M_BreezeFallingLeaves.M_BreezeFallingLeaves']
for path in materials:
 source=call('get_property_input',{'material':ref(path),'material_property':'MP_WorldPositionOffset'},MAT);assert source['expression'],path
report['animated_materials']=len(materials)
try:
 try:call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','startTransform':{'location':{'x':0,'y':300,'z':100},'rotation':{'pitch':0,'yaw':180,'roll':0}},'warmupSeconds':0}},APP)
 except RuntimeError as e:
  if 'PIE ended before warmup completed' not in str(e):raise
 assert call('IsPIERunning',{},APP)
 start=time.monotonic()
 camera=call('find_actors',{'name':'Woodland_FollowCamera','tag':'','collision_channels':[]},SCENE)[0]
 cc=call('get_components',{'actor':camera,'component_type':ref('/Script/Engine.CameraComponent')},ACT)[0]
 settings=json.loads(call('get_properties',{'instance':cc,'properties':['ProjectionMode','OrthoWidth']},OBJ));assert settings['OrthoWidth']==1200
 xf=call('get_actor_transform',{'actor':camera},ACT);assert abs(xf['rotation']['pitch']+34)<.01,xf
 report['camera']=settings;report['camera_transform']=xf
 leaf=call('find_actors',{'name':'Woodland_IntermittentLeaves','tag':'','collision_channels':[]},SCENE);assert len(leaf)==1
 for title,target in [('Calm',0),('Gust',6),('Calm_After',20)]:
  delay=target-(time.monotonic()-start)
  if delay>0:time.sleep(delay)
  capture=call('CaptureEditorImage',{},APP);(OUT/(title+'.png')).write_bytes(base64.b64decode(capture['data']));print('CAPTURED',title,flush=True)
 report['runtime_leaf_fields']=len(leaf)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 call('save_assets',{'asset_paths':[]},ASSET)
 call('set_properties',{'instance':ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),'values':json.dumps({'bThrottleCPUWhenNotForeground':True})},OBJ)
(OUT/'runtime.json').write_text(json.dumps(report,indent=2));print('BREEZE_RUNTIME_VERIFIED',flush=True)
