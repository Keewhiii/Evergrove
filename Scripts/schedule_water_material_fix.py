import unreal
def fix_forest_water(delta):
 if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world() is not None:return
 unreal.unregister_slate_post_tick_callback(water_fix_callback)
 for name in ['DeepWater','MidWater','ShallowWater']:
  mat=unreal.load_asset('/Game/Environment/ForestFeatures/M_'+name);mat.modify();mat.set_editor_property('tangent_space_normal',False)
  def node(name):return unreal.find_object(mat,name)
  for i in range(2):
   assert unreal.MaterialEditingLibrary.connect_material_expressions(node('MaterialExpressionWorldPosition_0'),'',node('MaterialExpressionComponentMask_'+str(i)),'')
   assert unreal.MaterialEditingLibrary.connect_material_expressions(node('MaterialExpressionAdd_'+str(i)),'',node('MaterialExpressionSine_'+str(i)),'')
  assert unreal.MaterialEditingLibrary.connect_material_property(node('MaterialExpressionNormalize_0'),'',unreal.MaterialProperty.MP_NORMAL)
  unreal.MaterialEditingLibrary.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)
 unreal.log('WATER_WORLD_SPACE_NORMALS_SAVED')
water_fix_callback=unreal.register_slate_post_tick_callback(fix_forest_water)
