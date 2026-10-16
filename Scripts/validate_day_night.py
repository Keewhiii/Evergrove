"""Runtime checks for clock progression, midnight, pause, and 3D lanterns."""
from build_companion_combat import *
import time, base64
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools';SM='editor_toolset.toolsets.static_mesh.StaticMeshTools'
OUT=ROOT/'Saved/DayNightAudit';OUT.mkdir(exist_ok=True)
def props(a,p):return call('set_properties',{'instance':a,'values':json.dumps(p)},OBJ)
def find(cls):return call('find_actors',{'name':'','tag':'','collision_channels':[],'actor_type':ref(cls)},SCENE)[0]
def sample():return json.loads(call('get_properties',{'instance':world,'properties':['TimeOfDayMinutes','DayNumber','ClockHour','ClockMinute','Daylight','IsNight','NightLightFactor','InteriorLightingActive']},OBJ))
report={}
probe=call('add_to_scene_from_asset',{'asset_path':'/Game/Tests/World/BP_GuildMovementProbe','name':'DayNight_TemporaryProbe','xform':{},'snap_to_ground':False},SCENE)
call('set_label',{'actor':probe,'label':'DayNight_TemporaryProbe'},ACT)
try:
    props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
    call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','startTransform':{'location':{'x':3000,'y':0,'z':100},'rotation':{'pitch':0,'yaw':180,'roll':0}},'warmupSeconds':0}},APP)
    world=find('/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld_C')
    camera=find('/Script/Engine.CameraActor')
    assert abs(call('get_actor_transform',{'actor':camera},ACT)['rotation']['pitch']+31)<.01
    live=call('find_actors',{'name':'DayNight_TemporaryProbe','tag':'','collision_channels':[]},SCENE)[0]
    time.sleep(.5); initial=sample();assert initial['DayNumber']==1 and 480<=initial['TimeOfDayMinutes']<500,initial
    before=sample();time.sleep(.5);after=sample();assert after['TimeOfDayMinutes']>before['TimeOfDayMinutes'];report['progress']=[before,after]
    props(world,{'ClockPaused':True,'TimeOfDayMinutes':720});time.sleep(.3);before=sample();time.sleep(.4);assert sample()['TimeOfDayMinutes']==before['TimeOfDayMinutes'];report['paused']=sample()
    props(world,{'TimeOfDayMinutes':1439,'DayNumber':4,'RealSecondsPerDay':60,'ClockPaused':False});time.sleep(.3)
    props(world,{'ClockPaused':True});rolled=sample();assert rolled['DayNumber']==5 and rolled['TimeOfDayMinutes']<60,rolled;report['midnight']=rolled
    cozy=find('/Game/Game/World/BP_CozyWoodland.BP_CozyWoodland_C');lanterns=[];planters=[]
    for c in call('get_components',{'actor':cozy,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT):
        p=json.loads(call('get_properties',{'instance':c,'properties':['StaticMesh','BodyInstance']},OBJ))
        if 'SM_GuildLantern3D' in str(p['StaticMesh']):
            assert p['BodyInstance']['collisionEnabled']=='NoCollision';lanterns.append(c)
        if '/Engine/BasicShapes/Cylinder' in str(p['StaticMesh']) or '/Engine/BasicShapes/Sphere' in str(p['StaticMesh']):planters.append(c)
    assert len(lanterns)==5,len(lanterns)
    assert not planters,planters
    bounds=call('get_bounds',{'mesh':ref('/Game/Environment/Lantern3D/SM_GuildLantern3D.SM_GuildLantern3D')},SM)
    assert bounds['max']['z']>270 and bounds['max']['y']-bounds['min']['y']>50,bounds
    lamps=call('get_components',{'actor':world,'component_type':ref('/Script/Engine.PointLightComponent')},ACT);assert len(lamps)==15
    sun=find('/Script/Engine.DirectionalLight');component=call('get_components',{'actor':sun,'component_type':ref('/Script/Engine.DirectionalLightComponent')},ACT)[0]
    for name,minutes in [('Dawn',375),('Noon',720),('Dusk',1065),('Midnight',0)]:
        props(world,{'TimeOfDayMinutes':minutes,'ClockPaused':True});time.sleep(1)
        state=sample();state['sun']=json.loads(call('get_properties',{'instance':component,'properties':['Intensity','LightColor']},OBJ))
        state['lamp']=json.loads(call('get_properties',{'instance':lamps[0],'properties':['Intensity']},OBJ));report[name]=state
        props(live,{'ScreenshotCommand':'HighResShot 1400x900 filename="'+str(OUT/(name+'.png')).replace('\\','/')+'"','ScreenshotRequested':True})
        time.sleep(.5)
        if name=='Midnight':
            props(world,{'ExteriorLightScale':0})
            time.sleep(.6)
            props(live,{'ScreenshotCommand':'HighResShot 1400x900 filename="'+str(OUT/'Midnight_PointLightsOff.png').replace('\\','/')+'"','ScreenshotRequested':True})
            time.sleep(.5)
            props(world,{'ExteriorLightScale':1})
            time.sleep(.2)
    assert report['Noon']['sun']['Intensity']>report['Midnight']['sun']['Intensity']*2
    assert report['Midnight']['lamp']['Intensity']>report['Noon']['lamp']['Intensity']*10
    assert report['Noon']['lamp']['Intensity']==0
    report['actual_light_comparison']=['Midnight.png','Midnight_PointLightsOff.png']
    fading=[]
    for minutes in [300,330,360,390,420,720,960,1020,1080,1140]:
        props(world,{'TimeOfDayMinutes':minutes});time.sleep(.15);fading.append(sample())
    assert [s['NightLightFactor'] for s in fading[:5]]==[1,.75,.5,.25,0],fading
    assert all(s['NightLightFactor']==0 for s in fading[4:7])
    assert 0<fading[7]['NightLightFactor']<fading[8]['NightLightFactor']<fading[9]['NightLightFactor']==1
    report['emission_fade']=fading
    player=find('/Game/Game/Characters/Player/Blueprints/BP_Player.BP_Player_C')
    xf=call('get_actor_transform',{'actor':player},ACT);xf['location']={'x':0,'y':-7200,'z':100}
    call('set_actor_transform',{'actor':player,'xform':xf,'worldspace':True},ACT)
    interior=[]
    for name,minutes in [('InteriorNoon',720),('InteriorMidnight',0)]:
        props(world,{'TimeOfDayMinutes':minutes});time.sleep(.7)
        assert sample()['InteriorLightingActive'],sample()
        camera_xf=call('get_actor_transform',{'actor':camera},ACT)
        assert abs(camera_xf['rotation']['pitch']+31)<.01,camera_xf
        values=json.loads(call('get_properties',{'instance':component,'properties':['Intensity','LightColor']},OBJ));values['rotation']=call('get_actor_transform',{'actor':sun},ACT)['rotation'];interior.append(values)
        props(live,{'ScreenshotCommand':'HighResShot 1400x900 filename="'+str(OUT/(name+'.png')).replace('\\','/')+'"','ScreenshotRequested':True});time.sleep(.5)
    assert interior[0]==interior[1],interior
    assert interior[0]['Intensity']==5
    report['stable_interior']=interior;report['removed_planter_components']=len(planters)
    following=[]
    for target in [{'x':0,'y':-7200,'z':100},{'x':1100,'y':-8500,'z':480}]:
        xf=call('get_actor_transform',{'actor':player},ACT);xf['location']=target
        call('set_actor_transform',{'actor':player,'xform':xf,'worldspace':True},ACT);time.sleep(1.2)
        actual=call('get_actor_transform',{'actor':player},ACT)['location']
        cam=call('get_actor_transform',{'actor':camera},ACT)
        assert abs(cam['location']['x']-actual['x'])<30,(actual,cam)
        assert abs(cam['location']['y']-actual['y']-2496)<30,(actual,cam)
        assert abs(cam['location']['z']-(1500+max(actual['z']-100,0)))<60,(actual,cam)
        assert abs(cam['rotation']['pitch']+31)<.01
        following.append({'player':actual,'camera':cam})
    assert following[1]['camera']['location']['x']-following[0]['camera']['location']['x']>1000
    report['interior_camera_follow']=following
    report['lantern_count']=len(lanterns);report['bounds']=bounds
    (OUT/'runtime.json').write_text(json.dumps(report,indent=2))
    print('DAY_NIGHT_AND_3D_LANTERNS_PASSED',flush=True)
finally:
    if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
    call('remove_from_scene',{'actor':probe},SCENE)
    props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':True})
