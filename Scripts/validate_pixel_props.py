"""Validate saved decorations and real PIE runtime dressing after the visual revision."""
from build_companion_combat import call,ref,ROOT,OBJ,ASSET,SCENE
import json,base64
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools';OUT=ROOT/'Saved/PixelPropsAudit'
try:
 try:call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','startTransform':{'location':{'x':0,'y':300,'z':100},'rotation':{'pitch':0,'yaw':180,'roll':0}},'warmupSeconds':0}},APP)
 except RuntimeError as e:
  if 'PIE ended before warmup completed' not in str(e):raise
 assert call('IsPIERunning',{},APP)
 camera=call('find_actors',{'name':'Woodland_FollowCamera','tag':'','collision_channels':[]},SCENE)[0]
 cc=call('get_components',{'actor':camera,'component_type':ref('/Script/Engine.CameraComponent')},ACT)[0]
 settings=json.loads(call('get_properties',{'instance':cc,'properties':['ProjectionMode','OrthoWidth']},OBJ));assert settings=={'ProjectionMode':'Orthographic','OrthoWidth':1450}
 cozy=call('find_actors',{'name':'BP_CozyWoodland','tag':'','collision_channels':[]},SCENE)
 counts={};errors=[]
 for actor in cozy:
  for c in call('get_components',{'actor':actor,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT):
   p=json.loads(call('get_properties',{'instance':c,'properties':['StaticMesh','BodyInstance']},OBJ));path=p['StaticMesh']['refPath']
   if '/PixelProps/' in path:
    name=path.split('.')[-1];counts[name]=counts.get(name,0)+1
    if p['BodyInstance']['collisionEnabled']!='NoCollision':errors.append(c)
 assert counts=={'SM_Prop_Lantern':5,'SM_Prop_Bush':10,'SM_Prop_Grass':10,'SM_Prop_Rock':5},counts
 assert not errors
 capture=call('CaptureEditorImage',{},APP);(OUT/'Game_Zoomed.png').write_bytes(base64.b64decode(capture['data']))
 report={'camera':settings,'runtime_props':counts,'collision_errors':errors};(OUT/'runtime.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 call('save_assets',{'asset_paths':[]},ASSET)
 call('set_properties',{'instance':ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),'values':json.dumps({'bThrottleCPUWhenNotForeground':True})},OBJ)
