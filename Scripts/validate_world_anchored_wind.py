"""Regression: wind stays in world space when the player and camera move."""
from build_companion_combat import call, ref, ROOT, SCENE, OBJ
import json, time, base64
APP = 'EditorToolset.EditorAppToolset'
ACT = 'editor_toolset.toolsets.actor.ActorTools'
out = ROOT / 'Saved/WoodlandWindFXAudit'
def find(name='', cls=None):
    args = {'name': name, 'tag': '', 'collision_channels': []}
    if cls: args['actor_type'] = ref(cls)
    return call('find_actors', args, SCENE)[0]
def xf(a): return call('get_actor_transform', {'actor': a}, ACT)
def move(a, x, y):
    t = xf(a); t['location'] = {'x': x, 'y': y, 'z': 100}
    call('set_actor_transform', {'actor': a, 'xform': t, 'worldspace': True}, ACT)
try:
    call('set_properties', {'instance': ref('/Script/UnrealEd.Default__EditorPerformanceSettings'), 'values': json.dumps({'bThrottleCPUWhenNotForeground': False})}, OBJ)
    call('StartPIE', {'options': {'bSimulate': False, 'playMode': 'PlayMode_InViewPort', 'warmupSeconds': 0}}, APP)
    player = find(cls='/Game/Game/Characters/Player/Blueprints/BP_Player.BP_Player_C')
    wind = find('Woodland_VisibleWind')
    camera = find(cls='/Script/Engine.CameraActor')
    samples = []
    for x, y in [(500, 0), (1850, 140), (3000, 440), (1850, -10000), (1850, 0)]:
        move(player, x, y); time.sleep(1)
        loc = xf(wind)['location']
        assert loc == {'x': 2000, 'y': 0, 'z': 0}, loc
        hidden = json.loads(call('get_properties', {'instance': wind, 'properties': ['bHidden']}, OBJ))['bHidden']
        assert hidden == (y < -5000), hidden
        samples.append({'player': xf(player)['location'], 'wind': loc, 'camera': xf(camera)['location'], 'hidden': hidden})
    assert abs(samples[2]['camera']['x'] - samples[0]['camera']['x']) > 1000, samples
    time.sleep(1)
    for i in range(2):
        cap = call('CaptureEditorImage', {}, APP)
        (out / ('WorldAnchoredWind_' + str(i) + '.png')).write_bytes(base64.b64decode(cap['data']))
        time.sleep(.7)
    (out / 'world_anchored_runtime.json').write_text(json.dumps(samples, indent=2))
    print('WORLD_ANCHORED_WIND_RUNTIME_PASSED', flush=True)
finally:
    if call('IsPIERunning', {}, APP): call('StopPIE', {}, APP)
    call('set_properties', {'instance': ref('/Script/UnrealEd.Default__EditorPerformanceSettings'), 'values': json.dumps({'bThrottleCPUWhenNotForeground': True})}, OBJ)
