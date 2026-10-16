import unreal as u,math
levels=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assert levels.load_level('/Game/Maps/L_EvergroveIntro')
for actor in actors.get_all_level_actors():
 if actor.get_actor_label().startswith('RuralNative_TemporaryProbe'):actors.destroy_actor(actor)
assert levels.save_current_level()
assert levels.load_level('/Game/Maps/L_EvergroveForest')
for actor in actors.get_all_level_actors():
 if actor.get_actor_label().startswith('Forest_FallenLog'):
  pos=actor.get_actor_location();actor.modify();actor.set_actor_rotation(u.Rotator(pitch=0,yaw=25+55*math.sin(pos.x*.013+pos.y*.019),roll=0),False)
assert levels.save_current_level()
u.log('LOG_ORIENTATION_POLISH_SAVED')
