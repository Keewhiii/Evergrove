import unreal,math
def clear_water_groundcover(delta):
 if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world() is not None:return
 unreal.unregister_slate_post_tick_callback(clear_water_callback)
 unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/L_EvergroveForest')
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);removed=0
 bodies=[(8500,2500,700,500),(4100,2600,230,170),(7950,-4300,260,190)]
 for a in actors.get_all_level_actors():
  if not a.get_actor_label().startswith(('Forest_Fern','Forest_Wildflowers')):continue
  p=a.get_actor_location();cx=5750+180*math.sin(p.y/1200)+90*math.sin(p.y/470);width=130+25*math.sin(p.y/700+.4)
  if abs(p.x-cx)<width*1.08 or any(((p.x-x)/rx)**2+((p.y-y)/ry)**2<1.1 for x,y,rx,ry in bodies):actors.destroy_actor(a);removed+=1
 unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True);unreal.log('WATER_GROUNDCOVER_CLEARED '+str(removed))
clear_water_callback=unreal.register_slate_post_tick_callback(clear_water_groundcover)
