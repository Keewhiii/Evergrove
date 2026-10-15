"""Animate the wind curve's shape: traveling coils, rolling loops and gentle undulation."""
from build_companion_combat import call,ref,ROOT,OBJ,ASSET,SCENE
from woodland_fx_graph import Graph,props,MAT
import json
F='/Game/Environment/WoodlandWindFX';SM='editor_toolset.toolsets.static_mesh.StaticMeshTools';ACT='editor_toolset.toolsets.actor.ActorTools';name='SM_FluidWindRibbonLocal';mesh=ref(F+'/'+name+'.'+name)
props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
if not call('exists',{'path':F+'/'+name},ASSET):call('import_file',{'folder_path':F,'asset_name':name,'source_file':str(ROOT/'ContentSource/WoodlandWindFX/FBX'/(name+'.fbx')),'import_materials':False,'import_textures':False,'combine_meshes':True},SM)
call('remove_collisions',{'mesh':mesh},SM)
m=ref(F+'/M_VisibleWind.M_VisibleWind');g=Graph(m)
travel=call('get_property_input',{'material':m,'material_property':'MP_WorldPositionOffset'},MAT)['expression']
for e in call('get_expressions',{'material_or_function':m},MAT):
 if 'ScalarParameter' in str(call('get_class',{'instance':e},OBJ)) and json.loads(call('get_properties',{'instance':e,'properties':['ParameterName']},OBJ))['ParameterName']=='CurlStrength':
  travel=next(p['expression'] for p in call('get_expression_inputs',{'material_or_function':m,'expression':travel},MAT) if p['input_name']=='A');break
time=g.n('Time');uv=g.n('TextureCoordinate');u=g.mask(uv,'G');world=g.n('WorldPosition');spatial=g.pair('DotProduct',world,g.vec('WindSpatialVariation',(.00037,.00023,0)))
endfade=g.sine(u,2);endfade=g.pair('Multiply',endfade,endfade)
center=g.add(g.mul(g.sine(g.pair('Add',g.mul(time,.11),spatial)),.18),.5)
delta=g.pair('Subtract',u,center);exponent=g.mul(g.pair('Multiply',delta,delta),-36)
bell=g.n('Power');g.wire(g.n('Constant',R=2),bell,'Base');g.wire(exponent,bell,'Exp');bell=g.pair('Multiply',bell,endfade)
angle=g.pair('Add',g.pair('Add',g.mul(u,2),g.mul(time,.35)),spatial)
curlx=g.pair('Multiply',g.mul(g.sine(g.add(angle,.25)),115),bell)
curly=g.pair('Multiply',g.mul(g.sine(angle),115),bell)
wave=g.sine(g.pair('Add',g.pair('Add',g.mul(u,1.3),g.mul(time,-.26)),spatial));wave=g.pair('Multiply',g.mul(wave,70),endfade)
dy=g.pair('Add',curly,wave);dz=g.pair('Multiply',g.mul(g.sine(g.pair('Add',g.mul(u,1.8),g.mul(time,.19))),16),endfade)
xy=g.n('AppendVector');g.wire(curlx,xy,'A');g.wire(dy,xy,'B');deform=g.n('AppendVector');g.wire(xy,deform,'A');g.wire(dz,deform,'B')
strength=g.n('ScalarParameter',ParameterName='CurlStrength',DefaultValue=1)
g.output(g.pair('Add',travel,g.pair('Multiply',deform,strength)),'MP_WorldPositionOffset');call('delete_unused_expressions',{'material':m},MAT);call('recompile',{'material_or_function':m},MAT)
for slot in call('get_material_slots',{'mesh':mesh},SM):call('set_material',{'mesh':mesh,'slot_name':slot,'material':m},SM)
a=call('find_actors',{'name':'Woodland_VisibleWind','tag':'','collision_channels':[]},SCENE)[0];c=call('get_components',{'actor':a,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)[0];props(c,{'StaticMesh':mesh['refPath'],'OverrideMaterials':[],'BoundsScale':2,'ForcedLodModel':1})
call('save_assets',{'asset_paths':[]},ASSET)
report={'segments_per_ribbon':192,'ribbons':6,'rolling_curl_radius_cm':115,'wave_amplitude_cm':70,'curl_turns_per_second':.35,'curl_strength':1,'triangles':call('get_triangle_count',{'mesh':mesh,'lod_index':0},SM)}
(ROOT/'Saved/WoodlandWindFXAudit/fluid_wind.json').write_text(json.dumps(report,indent=2));print('FLUID_WIND_AUTHORED '+json.dumps(report),flush=True)
