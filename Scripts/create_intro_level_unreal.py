"""Run with Unreal's PythonScript commandlet to create a clean menu world."""
import unreal
worlds=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert worlds.new_level('/Game/Maps/L_EvergroveIntro')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
mode=unreal.load_class(None,'/Game/Game/UI/BP_EvergroveIntroMode.BP_EvergroveIntroMode_C')
assert mode
world.get_world_settings().set_editor_property('default_game_mode',mode)
assert worlds.save_current_level()
unreal.log('EVERGROVE_CLEAN_INTRO_LEVEL_SAVED')
