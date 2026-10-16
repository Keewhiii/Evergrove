from build_companion_combat import *
import time
APP='EditorToolset.EditorAppToolset'
live=call('find_actors',{'name':'RuralNative_TemporaryProbe','tag':'','collision_channels':[]},SCENE)
print(live)
live=[a for a in live if 'UEDPIE' in a['refPath']][0]
call('set_properties',{'instance':live,'values':json.dumps({'ScreenshotRequested':True,'ScreenshotCommand':'py "E:/UE5 Projects/AdventureRPG/Scripts/schedule_forest_recovery.py"'})},OBJ)
time.sleep(1)
call('StopPIE',{},APP)
print('RECOVERY_TRIGGERED')
