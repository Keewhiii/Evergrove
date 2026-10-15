"""Refine existing gust leaves and provide independent per-town/route material presets."""
from build_companion_combat import call,ref,ROOT,OBJ,ASSET,SCENE
import json
F='/Game/Environment/BreezeWoodland';SM='editor_toolset.toolsets.static_mesh.StaticMeshTools';MAT='editor_toolset.toolsets.material.MaterialTools';MI='editor_toolset.toolsets.material_instance.MaterialInstanceTools';ACT='editor_toolset.toolsets.actor.ActorTools'
def props(o,p):return call('set_properties',{'instance':o,'values':json.dumps(p)},OBJ)
props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
m=ref(F+'/M_BreezeFallingLeaves.M_BreezeFallingLeaves');name='SM_DirectionalLeafField';mesh=ref(F+'/'+name+'.'+name)
if not call('exists',{'path':F+'/'+name},ASSET):call('import_file',{'folder_path':F,'asset_name':name,'source_file':str(ROOT/'ContentSource/BreezeWoodland/FBX'/(name+'.fbx')),'import_materials':False,'import_textures':False,'combine_meshes':True},SM)
call('remove_collisions',{'mesh':mesh},SM)
def n(t,p=None):
 o=call('add_expression',{'material_or_function':m,'expression_class':ref('/Script/Engine.MaterialExpression'+t)},MAT)
 if p:props(o,p)
 return o
def wire(a,b,p):call('connect_expressions',{'from_expression':a,'from_output_name':'','to_expression':b,'to_input_name':p},MAT)
def pair(t,a,b):
 o=n(t);wire(a,o,'A');wire(b,o,'B');return o
def vec(label,v):return n('VectorParameter',{'ParameterName':label,'DefaultValue':{'R':v[0],'G':v[1],'B':v[2],'A':1}})
expressions=call('get_expressions',{'material_or_function':m},MAT)
age=[e for e in expressions if call('get_class',{'instance':e},OBJ)['refPath'].endswith('MaterialExpressionFrac')][0]
flutter=[e for e in expressions if call('get_class',{'instance':e},OBJ)['refPath'].endswith('MaterialExpressionSine')][-1]
direction=n('ScalarParameter',{'ParameterName':'WindDirectionSign','DefaultValue':1})
fall=pair('Multiply',age,vec('FallTravel',(0,0,-510)))
horizontal=pair('Multiply',pair('Multiply',age,direction),vec('HorizontalTravel',(600,0,0)))
drift=pair('Multiply',flutter,vec('FlutterDistance',(35,16,4)))
offset=pair('Add',pair('Add',fall,horizontal),drift)
call('connect_to_output',{'expression':offset,'output_name':'','material_property':'MP_WorldPositionOffset'},MAT)
call('delete_unused_expressions',{'material':m},MAT);call('recompile',{'material_or_function':m},MAT)
presets={}
for label,sign in [('Left',-1),('Right',1)]:
 name='MI_BreezeLeaves_'+label;instance=ref(F+'/'+name+'.'+name)
 if not call('exists',{'path':F+'/'+name},ASSET):call('create',{'folder_path':F,'asset_name':name,'parent':m},MI)
 call('set_scalar_parameter',{'instance':instance,'name':'WindDirectionSign','value':sign},MI)
 assert call('get_scalar_parameter',{'instance':instance,'name':'WindDirectionSign'},MI)==sign
 presets[label]=instance
for slot in call('get_material_slots',{'mesh':mesh},SM):call('set_material',{'mesh':mesh,'slot_name':slot,'material':presets['Left']},SM)
actor=call('find_actors',{'name':'Woodland_IntermittentLeaves','tag':'','collision_channels':[]},SCENE)[0]
c=call('get_components',{'actor':actor,'component_type':ref('/Script/Engine.StaticMeshComponent')},ACT)[0]
props(c,{'StaticMesh':mesh['refPath'],'OverrideMaterials':[presets['Left']['refPath']],'BoundsScale':2,'CastShadow':False})
call('save_assets',{'asset_paths':[]},ASSET)
report={'mesh':mesh,'leaf_size_multiplier':1.5,'horizontal_travel_cm':600,'fall_travel_cm':510,'current_route_direction':'Left','presets':presets,'triangles':call('get_triangle_count',{'mesh':mesh,'lod_index':0},SM)}
out=ROOT/'Saved/BreezeWoodlandAudit';(out/'directional_leaves.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
