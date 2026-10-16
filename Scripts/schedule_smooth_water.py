import unreal
def finish_smooth_water(delta):
 if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world() is not None:return
 unreal.unregister_slate_post_tick_callback(smooth_water_callback)
 path='E:/UE5 Projects/AdventureRPG/Scripts/forest_water_surface.py'
 try:exec(compile(open(path,encoding='utf-8').read(),path,'exec'),{'REIMPORT_WATER':True})
 except Exception:
  import traceback
  unreal.log_error(traceback.format_exc())
smooth_water_callback=unreal.register_slate_post_tick_callback(finish_smooth_water)
