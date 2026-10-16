import unreal as u,json
from pathlib import Path
ROOT=Path('E:/UE5 Projects/AdventureRPG')
levels=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assert levels.load_level('/Game/Maps/L_EvergroveForest')
exec(compile((ROOT/'Scripts/forest_terrain_height.py').read_text(),'forest_terrain_height.py','exec'))
starts=[a for a in actors.get_all_level_actors() if isinstance(a,u.PlayerStart)]
assert len(starts)==1,len(starts)
a=starts[0];a.modify();a.set_actor_location(u.Vector(9200,1800,110+terrain_height(9200,1800)),False,False)
a.tags=[str(t) for t in a.tags if not str(t).startswith('TerrainBaseZ=')]+['TerrainBaseZ=110.0']
a.set_editor_property('is_spatially_loaded',False)
assert levels.save_current_level();assert u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
u.log('FOREST_VIEWPORT_PLAYERSTART_SAVED '+str(a.get_actor_location()))
