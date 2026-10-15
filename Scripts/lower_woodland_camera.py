"""Use a shallower 34-degree woodland view while preserving zoom and player framing."""
from build_companion_combat import call,ref,ROOT,OBJ,ASSET,SCENE,graph
import json,math
ACT='editor_toolset.toolsets.actor.ActorTools';WORLD='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
pitch=34;offset=round(1500/math.tan(math.radians(pitch)))
call('set_properties',{'instance':ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),'values':json.dumps({'bThrottleCPUWhenNotForeground':False})},OBJ)
source=(ROOT/'Saved/CombatAudit/UpdateCamera.dsl').read_text(encoding='utf-8')
for previous in ['1666.0','1800.0','2224.0']:source=source.replace('600.0) '+previous+') 1500.0','600.0) '+str(float(offset))+') 1500.0')
graph(WORLD,'UpdateCamera',source,[('Delta','float',None)])
camera=call('find_actors',{'name':'Woodland_FollowCamera','tag':'','collision_channels':[]},SCENE)[0]
xf=call('get_actor_transform',{'actor':camera},ACT);xf['rotation']={'pitch':-pitch,'yaw':-90,'roll':0};xf['location']={'x':0,'y':300+offset,'z':1500}
call('set_actor_transform',{'actor':camera,'xform':xf,'worldspace':True},ACT)
component=call('get_components',{'actor':camera,'component_type':ref('/Script/Engine.CameraComponent')},ACT)[0]
settings=json.loads(call('get_properties',{'instance':component,'properties':['ProjectionMode','OrthoWidth']},OBJ));assert settings['OrthoWidth']==1200
call('save_assets',{'asset_paths':[]},ASSET)
out=ROOT/'Saved/BreezeWoodlandAudit';(out/'camera_34.json').write_text(json.dumps({'pitch':-pitch,'follow_y_offset':offset,'settings':settings},indent=2));print('CAMERA_LOWERED',pitch,offset,settings,flush=True)
