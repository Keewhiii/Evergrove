from build_companion_combat import *
MODE='/Game/Game/UI/BP_EvergroveIntroMode.BP_EvergroveIntroMode_C'
GI='/Game/Game/UI/BP_EvergroveGameInstance.BP_EvergroveGameInstance_C'
call('save_assets',{'asset_paths':[]},ASSET)
call('save_assets',{'asset_paths':[call('get_current_level',{},SCENE)]},ASSET)
call('load_level',{'level_path':'/Game/Maps/L_EvergroveIntro'},SCENE)
settings=call('find_actors',{'name':'','tag':'','collision_channels':[],'actor_type':ref('/Script/Engine.WorldSettings')},SCENE)[0]
call('set_properties',{'instance':settings,'values':json.dumps({'DefaultGameMode':MODE})},OBJ)
call('save_assets',{'asset_paths':['/Game/Maps/L_EvergroveIntro']},ASSET)
call('save_assets',{'asset_paths':[]},ASSET)
call('set_properties',{'instance':ref('/Script/EngineSettings.Default__GameMapsSettings'),'values':json.dumps({'GameInstanceClass':GI,'GameDefaultMap':'/Game/Maps/L_EvergroveIntro.L_EvergroveIntro'})},OBJ)
p=ROOT/'Config/DefaultEngine.ini';s=p.read_text()
s=s.replace('GameDefaultMap=/Game/Maps/L_WoodlandBlockout','GameDefaultMap=/Game/Maps/L_EvergroveIntro')
if 'GameInstanceClass=' not in s:s=s.replace('EditorStartupMap=/Game/Maps/L_WoodlandBlockout','EditorStartupMap=/Game/Maps/L_WoodlandBlockout\nGameInstanceClass='+GI)
p.write_text(s)
print('INTRO_DEFAULT_MAP_CONFIGURED',flush=True)
