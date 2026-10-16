import unreal
def build_forest_when_stopped(delta):
 if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world() is not None:return
 unreal.unregister_slate_post_tick_callback(forest_level_callback)
 path='E:/UE5 Projects/AdventureRPG/Scripts/author_living_ponds_unreal.py'
 try:exec(compile(open(path,encoding='utf-8').read(),path,'exec'),{})
 except Exception:
  import traceback
  unreal.log_error(traceback.format_exc())
forest_level_callback=unreal.register_slate_post_tick_callback(build_forest_when_stopped)
