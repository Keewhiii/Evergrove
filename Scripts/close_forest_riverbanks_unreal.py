import unreal as u,json
from pathlib import Path
ROOT=Path('E:/UE5 Projects/AdventureRPG')
levels=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assert levels.load_level('/Game/Maps/L_EvergroveForest')
helper=(ROOT/'Scripts/author_rural_map_unreal.py').read_text();exec(helper[helper.index('mesh_cache={}'):helper.index('# A single continuous ground')])
exec(compile((ROOT/'Scripts/riverbank_thickets.py').read_text(),'riverbank_thickets.py','exec'))
existing=actors.get_all_level_actors()
for a in existing:
 if a.get_actor_label().startswith(('Forest_RiverbankTree','Forest_RiverbankThicket','Forest_RiverbankClosed')):actors.destroy_actor(a)
report=fill_riverbanks(place,collider,actors.get_all_level_actors())
assert levels.save_current_level();assert u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(ROOT/'Saved/SeparateForestAudit/riverbank_thickets.json').write_text(json.dumps(report,indent=2))
u.log('DENSE_CLOSED_RIVERBANKS_SAVED '+str(report))
