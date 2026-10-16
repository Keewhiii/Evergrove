"""Let the lantern point light escape its glass, and lower both camera views."""
from build_companion_combat import *
from woodland_fx_graph import Graph,props,MAT
import math
ACT='editor_toolset.toolsets.actor.ActorTools'
WORLD='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
m=ref('/Game/Environment/Lantern3D/M_LanternWarmGlass.M_LanternWarmGlass')
for expression in call('get_expressions',{'material_or_function':m},MAT):
    call('delete_expression',{'material_or_function':m,'expression':expression},MAT)
g=Graph(m);g.output(g.vec('GlassTint',(.6,.28,.06)),'MP_BaseColor')
night=g.n('CollectionParameter',Collection='/Game/Environment/DayNight/MPC_WorldClock.MPC_WorldClock',ParameterName='NightGlow')
g.output(g.mul(g.pair('Multiply',g.vec('WarmGlow',(1,.32,.08)),night),.5),'MP_EmissiveColor')
g.output(g.n('Constant',R=.4),'MP_Opacity');g.output(g.n('Constant',R=.25),'MP_Roughness')
props(m,{'BlendMode':'BLEND_Translucent','TwoSided':True,'ShadingModel':'MSM_DefaultLit','TranslucencyLightingMode':'TLM_Surface'})
call('recompile',{'material_or_function':m},MAT)
# Use the current authored graph; avoid stale pre-door camera migrations.
source=(ROOT/'Saved/CombatAudit/UpdateCamera.dsl').read_text(encoding='utf-8')
audit=ROOT/'Saved/DayNightAudit';audit.mkdir(exist_ok=True)
before=audit/'UpdateCamera_before_31.dsl'
if not before.exists():before.write_text(source,encoding='utf-8')
pitch=31;offset=round(1500/math.tan(math.radians(pitch)))
assert '(CallFunction|EnsureCozy)' in source and '(bind inside' in source, 'Expected current interior-aware camera source'
source=source.replace('2224.0',str(float(offset)))
source=source.replace('(Math|Float|Clamp(Float) x -980.0 980.0)','x').replace('(Math|Float|Clamp(Float) y -8360.0 -6260.0)','y')
graph(WORLD,'UpdateCamera',source,[('Delta','float',None)])
camera=call('find_actors',{'name':'Woodland_FollowCamera','tag':'','collision_channels':[]},SCENE)[0]
xf=call('get_actor_transform',{'actor':camera},ACT);xf['rotation']={'pitch':-pitch,'yaw':-90,'roll':0};xf['location']={'x':0,'y':300+offset,'z':1500}
call('set_actor_transform',{'actor':camera,'xform':xf,'worldspace':True},ACT)
component=call('get_components',{'actor':camera,'component_type':ref('/Script/Engine.CameraComponent')},ACT)[0]
settings=json.loads(call('get_properties',{'instance':component,'properties':['ProjectionMode','OrthoWidth']},OBJ))
call('compile_blueprint',{'blueprint':ref(WORLD),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[]},ASSET)
(audit/'camera_31.json').write_text(json.dumps({'pitch':-pitch,'follow_y_offset':offset,'settings':settings},indent=2))
print('LANTERN_GLASS_AND_31_DEGREE_CAMERA_SAVED',offset,settings,flush=True)
