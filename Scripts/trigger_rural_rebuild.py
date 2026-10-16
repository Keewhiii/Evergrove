from build_companion_combat import *
import time,sys
APP='EditorToolset.EditorAppToolset'
T='/Game/Tests/World/BP_GuildMovementProbe.BP_GuildMovementProbe'
call('load_level',{'level_path':'/Game/Maps/L_EvergroveIntro'},SCENE)
probe=call('add_to_scene_from_asset',{'asset_path':T.split('.')[0],'name':'RuralNative_TemporaryProbe','xform':{},'snap_to_ground':False},SCENE)
call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':0}},APP)
live=call('find_actors',{'name':'RuralNative_TemporaryProbe','tag':'','collision_channels':[]},SCENE)[0]
native_script=sys.argv[1] if len(sys.argv)>1 else 'schedule_rural_rebuild.py'
call('set_properties',{'instance':live,'values':json.dumps({'ScreenshotRequested':True,'ScreenshotCommand':'py "E:/UE5 Projects/AdventureRPG/Scripts/'+native_script+'"'})},OBJ)
time.sleep(.5)
call('StopPIE',{},APP)
print('NATIVE_REBUILD_TRIGGERED',flush=True)
