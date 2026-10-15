"""Capture actual orthographic PIE and confirm camera/flat-tree assets at runtime."""
from build_companion_combat import call, ROOT, SCENE, ref, OBJ
import json,base64
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools'
OUT=ROOT/'Saved/LayeredWoodlandAudit';OUT.mkdir(exist_ok=True)
if call('IsPIERunning',{},APP):raise RuntimeError('Stop the active play session first')
try:
    try:call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','startTransform':{'location':{'x':0,'y':300,'z':100},'rotation':{'pitch':0,'yaw':180,'roll':0}},'warmupSeconds':0}},APP)
    except RuntimeError as e:
        if 'PIE ended before warmup completed' not in str(e):raise
    if not call('IsPIERunning',{},APP):raise RuntimeError('PIE did not start')
    camera=call('find_actors',{'name':'Woodland_FollowCamera','tag':'','collision_channels':[]},SCENE)[0]
    component=call('get_components',{'actor':camera,'component_type':ref('/Script/Engine.CameraComponent')},ACT)[0]
    settings=json.loads(call('get_properties',{'instance':component,'properties':['ProjectionMode','OrthoWidth']},OBJ))
    if settings['ProjectionMode']!='Orthographic':raise RuntimeError('Gameplay camera is not orthographic')
    capture=call('CaptureEditorImage',{},APP)
    (OUT/'Game_Orthographic.png').write_bytes(base64.b64decode(capture['data']))
    (OUT/'runtime_camera.json').write_text(json.dumps(settings,indent=2))
    print('ORTHOGRAPHIC_RUNTIME_VERIFIED '+json.dumps(settings),flush=True)
finally:
    if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
