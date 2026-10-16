import unreal as u,json,math
from pathlib import Path
ROOT=Path('E:/UE5 Projects/AdventureRPG');F='/Game/Environment/ForestAtmosphere'
a=u.EditorAssetLibrary;mel=u.MaterialEditingLibrary;actors=u.get_editor_subsystem(u.EditorActorSubsystem);levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert levels.load_level('/Game/Maps/L_EvergroveForest')
task=u.AssetImportTask();task.filename=str(ROOT/'ContentSource/ForestAtmosphere/SM_CanopyFallingLeaves.obj');task.destination_path=F;task.destination_name='SM_CanopyFallingLeaves';task.automated=True;task.save=True;task.replace_existing=True
options=u.FbxImportUI();options.import_materials=False;options.import_textures=False;options.import_mesh=True;options.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;options.static_mesh_import_data.combine_meshes=True;options.static_mesh_import_data.auto_generate_collision=False;task.options=options
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);mesh=u.load_asset(F+'/SM_CanopyFallingLeaves');assert mesh
mat=u.load_asset(F+'/M_CanopyFallingLeaves') or u.AssetToolsHelpers.get_asset_tools().create_asset('M_CanopyFallingLeaves',F,u.Material,u.MaterialFactoryNew())
mat.modify();mel.delete_all_material_expressions(mat)
def expr(cls,**props):
 n=mel.create_material_expression(mat,getattr(u,'MaterialExpression'+cls))
 for k,v in props.items():n.set_editor_property(k,v)
 return n
def wire(x,y,pin):assert mel.connect_material_expressions(x,'',y,pin)
def custom(code,names,typ):
 inputs=[]
 for name in names:
  item=u.CustomInput();item.set_editor_property('input_name',name);inputs.append(item)
 return expr('Custom',code=code,inputs=inputs,output_type=typ)
pos=expr('WorldPosition');clock=expr('Time');uv=expr('TextureCoordinate')
# Terrain height is supplied by the same analytic height function as the ground mesh.
height_code=(ROOT/'Scripts/forest_elevation.hlsl').read_text() if (ROOT/'Scripts/forest_elevation.hlsl').exists() else 'return 0.0;'
ground=custom(height_code,['Position'],u.CustomMaterialOutputType.CMOT_FLOAT1);wire(pos,ground,'Position')
fall=custom((ROOT/'Scripts/forest_canopy_fall.hlsl').read_text(),['Position','Clock','UV','Ground'],u.CustomMaterialOutputType.CMOT_FLOAT3)
for node,pin in [(pos,'Position'),(clock,'Clock'),(uv,'UV'),(ground,'Ground')]:wire(node,fall,pin)
mel.connect_material_property(fall,'',u.MaterialProperty.MP_WORLD_POSITION_OFFSET)
color=custom('float3 leaf=lerp(float3(0.10,0.22,0.025),float3(0.27,0.39,0.075),UV.x);return leaf*(0.82+0.18*UV.y);',['UV'],u.CustomMaterialOutputType.CMOT_FLOAT3);wire(uv,color,'UV');mel.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
mask=custom('float age=frac(Clock/(12.0+UV.x*6.0)+UV.x);return smoothstep(0.0,0.035,age)*(1.0-smoothstep(0.94,0.995,age))*step(frac(UV.x*71.31),0.55);',['Clock','UV'],u.CustomMaterialOutputType.CMOT_FLOAT1);wire(clock,mask,'Clock');wire(uv,mask,'UV');mel.connect_material_property(mask,'',u.MaterialProperty.MP_OPACITY_MASK)
rough=expr('Constant',r=.85);mel.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
mat.set_editor_property('blend_mode',u.BlendMode.BLEND_MASKED);mat.set_editor_property('two_sided',True);mat.set_editor_property('opacity_mask_clip_value',.1);mel.recompile_material(mat);a.save_loaded_asset(mat)
mesh.set_material(0,mat);mesh.set_editor_property('positive_bounds_extension',u.Vector(250,80,50));mesh.set_editor_property('negative_bounds_extension',u.Vector(300,80,800));u.get_editor_subsystem(u.StaticMeshEditorSubsystem).remove_collisions(mesh);a.save_loaded_asset(mesh)
for actor in actors.get_all_level_actors():
 if actor.get_actor_label().startswith(('Forest_CanopyLeaves','Forest_WindTile')):actors.destroy_actor(actor)
 elif actor.get_actor_label()=='Woodland_IntermittentLeaves':actor.modify();actor.set_actor_hidden_in_game(True);actor.set_is_temporarily_hidden_in_editor(True)
def place(label,mesh,pos):
 actor=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*pos));actor.set_actor_label(label);actor.set_folder_path('Forest Atmosphere');actor.set_editor_property('is_spatially_loaded',False);actor.tags=['ForestAtmosphere']
 c=actor.static_mesh_component;c.set_static_mesh(mesh);c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION);c.set_editor_property('can_ever_affect_navigation',False);c.set_cast_shadow(False);c.set_editor_property('bounds_scale',2.0)
 return actor
place('Forest_CanopyLeaves',mesh,(0,0,0))
wind=u.load_asset('/Game/Environment/WoodlandWindFX/SM_FluidWindRibbonLocal')
for x in [2400,4900,7400,9900,12400]:
 for y in [-5200,-2800,-400,2000,4400]:place('Forest_WindTile',wind,(x,y,0))
# Upgrade existing logs in place so their scene transforms and references survive.
task=u.AssetImportTask();task.filename=str(ROOT/'ContentSource/ForestFeatures/SM_ForestCartoonLog.obj');task.destination_path='/Game/Environment/ForestFeatures';task.destination_name='SM_ForestCartoonLog';task.automated=True;task.save=True;task.replace_existing=True;task.options=options
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);log=u.load_asset('/Game/Environment/ForestFeatures/SM_ForestCartoonLog')
for i,slot in enumerate(log.get_editor_property('static_materials')):log.set_material(i,u.load_asset('/Game/Environment/RuralVillage/M_Rural_'+str(slot.get_editor_property('material_slot_name'))))
u.get_editor_subsystem(u.StaticMeshEditorSubsystem).remove_collisions(log);a.save_loaded_asset(log)
for actor in actors.get_all_level_actors():
 if actor.get_actor_label().startswith('Forest_FallenLog'):
  pos=actor.get_actor_location();yaw=25+55*math.sin(pos.x*.013+pos.y*.019)
  actor.modify();actor.set_actor_rotation(u.Rotator(pitch=0,yaw=yaw,roll=0),False)
assert levels.save_current_level();assert u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
u.log('FOREST_WIDE_CANOPY_FALL_AND_CARTOON_LOGS_SAVED')
