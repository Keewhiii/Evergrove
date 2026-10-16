"""Connect progressive window/lantern emission, stable interiors, and remove pots."""
from build_companion_combat import *
from woodland_fx_graph import Graph, props, MAT
import re
ACT='editor_toolset.toolsets.actor.ActorTools'
collection=ref('/Game/Environment/DayNight/MPC_WorldClock.MPC_WorldClock')
props(collection,{'ScalarParameters':[
 {'ParameterName':'NightBrightness','DefaultValue':1,'Id':'3a1d82c5-4c25-764a-6e24-0dae12345678'},
 {'ParameterName':'NightGlow','DefaultValue':0,'Id':'7a1d82c5-4c25-764a-6e24-0dae12345678'}]})
for path in ['/Game/Environment/Lantern3D/M_LanternWarmGlass.M_LanternWarmGlass','/Game/Environment/GuildHall/M_Guild_Glass.M_Guild_Glass']:
    m=ref(path);expressions=call('get_expressions',{'material_or_function':m},MAT)
    if any('CollectionParameter' in str(e) for e in expressions):continue
    source=call('get_property_input',{'material':m,'material_property':'MP_EmissiveColor'},MAT)
    g=Graph(m);param=g.n('CollectionParameter',Collection=collection['refPath'],ParameterName='NightGlow')
    mul=g.n('Multiply');g.wire(source['expression'],mul,'A',source.get('output_name',''));g.wire(param,mul,'B');g.output(mul,'MP_EmissiveColor');call('recompile',{'material_or_function':m},MAT)
name='GuildInterior_StableLightingZone'
actors=call('find_actors',{'name':name,'tag':'','collision_channels':[]},SCENE)
if actors:zone=actors[0]
else:
    zone=call('add_to_scene_from_asset',{'asset_path':'/Engine/BasicShapes/Cube','name':name,'xform':{'location':{'x':0,'y':-7300,'z':550},'scale':{'x':30,'y':30,'z':13}},'snap_to_ground':False},SCENE)
    call('set_label',{'actor':zone,'label':name},ACT)
    call('add_tag',{'actor':zone,'tag':'StableInteriorLighting'},ACT)
    call('set_actor_folder',{'actor':zone,'folder_path':'Woodland/Guild Interior/Lighting'},SCENE)
component=call('get_components',{'actor':zone,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)[0]
props(component,{'bVisible':False,'bHiddenInGame':True,'bUseDefaultCollision':False,'BodyInstance':{'CollisionProfileName':'NoCollision','CollisionEnabled':'NoCollision'},'bCanEverAffectNavigation':False,'CastShadow':False})
cozy='/Game/Game/World/BP_CozyWoodland.BP_CozyWoodland'
graph(cozy,'Dress0','(fn Dress0 ())')
graph(cozy,'EventGraph','''(event EventBeginPlay
 (bind root (AddComponent|Common|AddSceneComponent))
 (CallFunction|Dress1)
 (CallFunction|Dress2))''')
source=call('read_graph_dsl',{'graph':ref(cozy+':Dress1')})
out=ROOT/'Saved/DayNightAudit/Dress1_before_remove_planters.dsl'
if not out.exists():out.write_text(source,encoding='utf-8')
lines=source.splitlines();first=next(i for i,line in enumerate(lines) if 'SM_GuildLantern3D' in line)
source='(fn Dress1 ()\n'+'\n'.join(lines[first:])
source=re.sub(r'\(CallFunction\|Part (\(Math\|Vector\|MakeVector [^)]*\)) (\(Math\|Vector\|MakeVector [^)]*\)) ("[^"]*") ("[^"]*")\)',r'(CallFunction|Part :Position \1 :Scale \2 :Mesh \3 :Material \4)',source)
graph(cozy,'Dress1',source)
call('compile_blueprint',{'blueprint':ref(cozy),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[]},ASSET)
print('PROGRESSIVE_EMISSION_INTERIOR_ZONE_AND_POTS_REMOVED',flush=True)
