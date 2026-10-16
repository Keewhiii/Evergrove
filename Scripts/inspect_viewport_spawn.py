from build_companion_combat import *
ACT='editor_toolset.toolsets.actor.ActorTools'
for cls in ['/Script/Engine.PlayerStart','/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld_C']:
 actors=call('find_actors',{'name':'','tag':'','collision_channels':[],'actor_type':ref(cls)},SCENE)
 for a in actors:print(a,call('get_actor_transform',{'actor':a},ACT))
print('PLAYER_BEGIN',call('read_graph_dsl',{'graph':ref(PLAYER+':EventGraph')})[:7000])
print('PLAY_SETTINGS',call('get_properties',{'instance':ref('/Script/UnrealEd.Default__LevelEditorPlaySettings'),'properties':['LastExecutedPlayModeLocation','PlayNetMode','bOnlyLoadVisibleLevelsInPIE']},OBJ))
