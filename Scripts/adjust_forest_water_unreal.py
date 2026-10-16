import unreal as u,math
from pathlib import Path
root=Path('E:/UE5 Projects/AdventureRPG')
levels=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assert levels.load_level('/Game/Maps/L_EvergroveForest')
exec(compile((root/'Scripts/forest_water_surface.py').read_text(),'forest_water_surface.py','exec'),{'REIMPORT_WATER':True})
for actor in actors.get_all_level_actors():
 if actor.get_actor_label().startswith('Forest_RiverBank'):
  pos=actor.get_actor_location();scale=actor.get_actor_scale3d();scale.x=(130+25*math.sin(pos.y/700+.4))*1.8/100
  actor.modify();actor.set_actor_scale3d(scale)
assert levels.save_current_level();assert u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
u.log('CALM_WATER_AND_NARROW_BRIDGE_CHANNEL_SAVED')
