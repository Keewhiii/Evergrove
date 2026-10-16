import unreal as u,math
from pathlib import Path
ROOT=Path('E:/UE5 Projects/AdventureRPG');F='/Game/Environment/ForestFeatures'
levels=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem);assets=u.EditorAssetLibrary;mel=u.MaterialEditingLibrary
assert levels.load_level('/Game/Maps/L_EvergroveForest')
exec(compile((ROOT/'Scripts/forest_water_surface.py').read_text(),'forest_water_surface.py','exec'),{'STANDING_WATER_ONLY':True})
materials={}
for name,rgb in {'PadLight':(.12,.28,.045),'PadDark':(.065,.19,.035),'Flower':(.77,.68,.53),'Center':(.65,.40,.065)}.items():
 mat=u.load_asset(F+'/M_Lily_'+name) or u.AssetToolsHelpers.get_asset_tools().create_asset('M_Lily_'+name,F,u.Material,u.MaterialFactoryNew())
 mat.modify();mel.delete_all_material_expressions(mat)
 color=mel.create_material_expression(mat,u.MaterialExpressionConstant3Vector);color.set_editor_property('constant',u.LinearColor(*rgb,1));mel.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
 rough=mel.create_material_expression(mat,u.MaterialExpressionConstant);rough.set_editor_property('r',.65);mel.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
 t=mel.create_material_expression(mat,u.MaterialExpressionTime);pos=mel.create_material_expression(mat,u.MaterialExpressionWorldPosition)
 inputs=[]
 for name2 in ['Clock','Position']:
  item=u.CustomInput();item.set_editor_property('input_name',name2);inputs.append(item)
 motion=mel.create_material_expression(mat,u.MaterialExpressionCustom);motion.set_editor_property('inputs',inputs);motion.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT3);motion.set_editor_property('code','float p=Position.x*0.005+Position.y*0.008;return float3(sin(Clock*0.25+p)*1.5,cos(Clock*0.21+p)*1.0,sin(Clock*0.6+p)*0.65);')
 mel.connect_material_expressions(t,'',motion,'Clock');mel.connect_material_expressions(pos,'',motion,'Position');mel.connect_material_property(motion,'',u.MaterialProperty.MP_WORLD_POSITION_OFFSET)
 mat.set_editor_property('two_sided',True);mel.recompile_material(mat);assets.save_loaded_asset(mat);materials[name]=mat
options=u.FbxImportUI();options.import_materials=False;options.import_textures=False;options.import_mesh=True;options.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;options.static_mesh_import_data.combine_meshes=True;options.static_mesh_import_data.auto_generate_collision=False
task=u.AssetImportTask();task.filename=str(ROOT/'ContentSource/ForestFeatures/SM_ForestLilyPatch.obj');task.destination_path=F;task.destination_name='SM_ForestLilyPatch';task.automated=True;task.save=True;task.replace_existing=True;task.options=options
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);mesh=u.load_asset(F+'/SM_ForestLilyPatch');assert mesh
for i,slot in enumerate(mesh.get_editor_property('static_materials')):mesh.set_material(i,materials[str(slot.get_editor_property('material_slot_name'))])
u.get_editor_subsystem(u.StaticMeshEditorSubsystem).remove_collisions(mesh);assets.save_loaded_asset(mesh)
for actor in actors.get_all_level_actors():
 if actor.get_actor_label().startswith('Forest_LilyPatch'):actors.destroy_actor(actor)
for x,y,size,yaw in [(8900,2680,1,23),(8030,2470,.8,147),(4210,2670,.55,81),(7840,-4380,.65,212)]:
 actor=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(x,y,6),u.Rotator(pitch=0,yaw=yaw,roll=0));actor.set_actor_label('Forest_LilyPatch');actor.set_folder_path('Forest Water Detail');actor.set_editor_property('is_spatially_loaded',False)
 c=actor.static_mesh_component;c.set_static_mesh(mesh);c.set_world_scale3d(u.Vector(size,size,size));c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION);c.set_editor_property('can_ever_affect_navigation',False);c.set_cast_shadow(False)
assert levels.save_current_level();assert u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
u.log('LIVING_LAKE_AND_PONDS_SAVED')
