"""Import solid lantern and replace the five runtime sprite lanterns."""
from build_companion_combat import *
from woodland_fx_graph import Graph, props, MAT
SM='editor_toolset.toolsets.static_mesh.StaticMeshTools'
F='/Game/Environment/Lantern3D'; name='SM_GuildLantern3D'; mesh=ref(F+'/'+name+'.'+name)
if not call('exists',{'path':F+'/'+name},ASSET):
    call('import_file',{'folder_path':F,'asset_name':name,'source_file':str(ROOT/'ContentSource/Lantern3D/SM_GuildLantern.obj'),'import_materials':False,'import_textures':False,'combine_meshes':True},SM)
call('remove_collisions',{'mesh':mesh},SM)
glass=ref(F+'/M_LanternWarmGlass.M_LanternWarmGlass')
if not call('exists',{'path':F+'/M_LanternWarmGlass'},ASSET):
    call('create_material',{'folder_path':F,'asset_name':'M_LanternWarmGlass'},MAT)
    g=Graph(glass); color=g.vec('WarmGlass',(1,.48,.12));g.output(color,'MP_BaseColor');g.output(g.mul(color,3),'MP_EmissiveColor');g.output(g.n('Constant',R=.35),'MP_Roughness')
    call('recompile',{'material_or_function':glass},MAT)
for slot in call('get_material_slots',{'mesh':mesh},SM):
    mat=glass if 'Glass' in slot else ref('/Game/Environment/GuildHall/M_Guild_'+slot+'.M_Guild_'+slot)
    call('set_material',{'mesh':mesh,'slot_name':slot,'material':mat},SM)
print('LANTERN_BOUNDS',call('get_bounds',{'mesh':mesh},SM),flush=True)
cozy='/Game/Game/World/BP_CozyWoodland.BP_CozyWoodland'
target=ref(cozy+':Dress1');source=call('read_graph_dsl',{'graph':target})
backup=ROOT/'Saved/CombatAudit/Dress1_before_3d_lantern.dsl'
if not backup.exists():backup.write_text(source,encoding='utf-8')
source=backup.read_text(encoding='utf-8')
import re
source=re.sub(r'\(CallFunction\|Part (\(Math\|Vector\|MakeVector [^)]*\)) (\(Math\|Vector\|MakeVector [^)]*\)) ("[^"]*") ("[^"]*")\)',r'(CallFunction|Part :Position \1 :Scale \2 :Mesh \3 :Material \4)',source)
source=source.replace('/Game/Environment/PixelProps/SM_Prop_Lantern.SM_Prop_Lantern',mesh['refPath'])
# Part overrides slot zero; explicitly match its imported material.
first=call('get_material_slots',{'mesh':mesh},SM)[0]
override=glass['refPath'] if 'Glass' in first else '/Game/Environment/GuildHall/M_Guild_'+first+'.M_Guild_'+first
source=source.replace('/Game/Environment/PixelProps/M_Prop_Lantern.M_Prop_Lantern',override)
graph(cozy,'Dress1',source)
call('compile_blueprint',{'blueprint':ref(cozy),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[]},ASSET)
print('GUILD_LANTERNS_IMPORTED',flush=True)
