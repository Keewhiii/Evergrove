import unreal
def finish_hunter_placement(delta):
 if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world() is not None:return
 unreal.unregister_slate_post_tick_callback(hunter_placement_callback)
 unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/L_EvergroveStart')
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 for a in actors.get_all_level_actors():
  label=a.get_actor_label()
  p=a.get_actor_location()
  if label.startswith(('Forest_Tree','Tree_Trunk','Forest_ThicketBarrier')) and 8700<p.x<9700 and 1800<p.y<3200:
   actors.destroy_actor(a);continue
  for c in a.get_components_by_class(unreal.StaticMeshComponent):
   a.modify();c.modify()
   solid=c.get_editor_property('can_ever_affect_navigation')
   c.set_editor_property('use_default_collision',False)
   c.set_collision_profile_name('BlockAll' if solid else 'NoCollision')
   c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if solid else unreal.CollisionEnabled.NO_COLLISION)
   if label.startswith('Forest_Tree') and a.get_actor_location().x>4500:c.set_cast_shadow(False)
  if label.startswith('Forest_TrailMarker') and 'ForestMarkerPolished' not in [str(t) for t in a.tags]:
   a.modify();p=a.get_actor_location()
   if abs(p.y-100)<1 or abs(p.y+900)<1:p.x+=230
   else:p.y+=230
   a.set_actor_location(p,False,False);a.tags=list(a.tags)+['ForestMarkerPolished']
  if a.get_actor_label()=='Village_Luna':
   a.modify();a.set_actor_location(unreal.Vector(-580,-22200,100),False,False)
  if a.get_actor_label()=='Village_Rein':
   a.modify();a.set_actor_location(unreal.Vector(9010,1740,100),False,False)
 import json
 from pathlib import Path
 layout_path=Path('E:/UE5 Projects/AdventureRPG/ContentSource/RuralVillage/layout.json')
 layout=json.loads(layout_path.read_text());layout['hunter']=[9010,1740]
 labels={a.get_actor_label() for a in actors.get_all_level_actors()}
 for room in layout['interiors']:
  label=room['building']+'_InteriorBackdrop'
  if label in labels:continue
  x,y,z=room['center'];w,d=room['size']
  a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,y,-45));a.set_actor_label(label);a.set_folder_path('Interiors');a.set_editor_property('is_spatially_loaded',False)
  c=a.static_mesh_component;c.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));c.set_world_scale3d(unreal.Vector((w+3500)/100,(d+5000)/100,.08));c.set_material(0,unreal.load_asset('/Game/Environment/RuralVillage/M_Rural_Iron'));c.set_editor_property('use_default_collision',False);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);c.set_editor_property('can_ever_affect_navigation',False)
 layout_path.write_text(json.dumps(layout,indent=2))
 unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 unreal.log('HUNTER_AND_RECEPTION_PLACEMENT_SAVED')
hunter_placement_callback=unreal.register_slate_post_tick_callback(finish_hunter_placement)
