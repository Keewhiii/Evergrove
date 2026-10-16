"""Run native editor authoring once PIE has ended, in the owning editor process."""
import unreal
def rebuild_rural_after_pie(delta):
 if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world() is not None:return
 unreal.unregister_slate_post_tick_callback(rural_rebuild_callback)
 path='E:/UE5 Projects/AdventureRPG/Scripts/author_rural_map_unreal.py'
 try:
  exec(compile(open(path,encoding='utf-8').read(),path,'exec'),{'KEEP_EDITOR_OPEN':True})
  unreal.log('OWNING_EDITOR_RURAL_REBUILD_COMPLETE')
 except Exception:
  import traceback
  unreal.log_error(traceback.format_exc())
rural_rebuild_callback=unreal.register_slate_post_tick_callback(rebuild_rural_after_pie)
unreal.log('OWNING_EDITOR_RURAL_REBUILD_SCHEDULED')
