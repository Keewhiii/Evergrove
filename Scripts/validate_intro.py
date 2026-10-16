"""Exercise menu actions in PIE using isolated saves; retain visual evidence."""
from build_companion_combat import *
import time
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools'
M='/Game/Game/UI/BP_EvergroveIntroHUD.BP_EvergroveIntroHUD'
GI='/Game/Game/UI/BP_EvergroveGameInstance.BP_EvergroveGameInstance'
T='/Game/Tests/World/BP_IntroValidation.BP_IntroValidation'
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
OUT=ROOT/'Saved/EvergroveIntroAudit';OUT.mkdir(exist_ok=True)
def get(o,keys):return json.loads(call('get_properties',{'instance':o,'properties':keys},OBJ))
def props(o,values):return call('set_properties',{'instance':o,'values':json.dumps(values)},OBJ)
def find(cls):return call('find_actors',{'name':'','tag':'','collision_channels':[],'actor_type':ref(cls+'_C')},SCENE)
def action(n):
 props(live,{'Action':n,'Requested':True});time.sleep(.25)
def shot(name):
 props(live,{'Action':6,'ScreenshotCommand':'HighResShot 1600x900 filename="'+str(OUT/(name+'.png')).replace('\\','/')+'"','Requested':True});time.sleep(.4)
report={}
probe=call('add_to_scene_from_asset',{'asset_path':T.split('.')[0],'name':'Intro_TemporaryProbe','xform':{},'snap_to_ground':False},SCENE)
try:
 props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
 call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':0}},APP);time.sleep(.6)
 live=find(T)[0];action(4);menu=get(live,['Menu'])['Menu'];instance=get(menu,['Instance'])['Instance']
 report['initial']=get(menu,['HasSave','SaveSummary','Page','Selected'])
 controller=call('find_actors',{'name':'','tag':'','collision_channels':[],'actor_type':ref('/Script/Engine.PlayerController')},SCENE)[0]
 report['mouse_input']=get(controller,['bEnableClickEvents','bEnableMouseOverEvents','bShowMouseCursor'])
 assert all(report['mouse_input'].values()),report
 shot('Title')
 props(instance,{'MenuSaveSlot':'Evergrove_Absent_Validation_20261015'})
 action(0);assert not get(menu,['HasSave'])['HasSave']
 report['no_save']=get(menu,['HasSave','SaveSummary']);shot('Title_NoSave')
 props(menu,{'Selected':0});action(10);assert get(menu,['Selected'])['Selected']==2
 props(menu,{'Selected':0})
 props(instance,{'MenuSaveSlot':'AdventureRPG_ClockContinuityValidation_20261015'})
 action(0);assert get(menu,['HasSave'])['HasSave']
 report['saved_summary']=get(menu,['HasSave','SaveSummary']);shot('Title_WithSave')
 time.sleep(1);shot('Title_Animated')
 props(menu,{'Selected':0});action(1);assert get(menu,['Page'])['Page']==2
 shot('NewGameConfirm');action(2)
 action(9);assert get(menu,['Page'])['Page']==1
 props(menu,{'Selected':0,'OptVolume':.5});action(14)
 assert get(menu,['Selected'])['Selected']==5
 action(11);assert abs(get(menu,['OptVolume'])['OptVolume']-.55)<1e-9
 action(12);assert abs(get(menu,['OptVolume'])['OptVolume']-.5)<1e-9
 action(13);assert abs(get(menu,['OptVolume'])['OptVolume']-.55)<1e-9
 report['options_navigation']={'arrow_adjustment':True,'mouse_hover':True,'mouse_arrow_action':True}
 shot('Options')
 # Persist preference values only into a dedicated validation slot.
 original=get(instance,['OptionsSlot','MasterVolume','Brightness','MenuMotion'])
 props(instance,{'OptionsSlot':'Evergrove_Options_Validation_20261015'})
 props(menu,{'OptVolume':.65,'OptBrightness':.95,'OptMotion':False})
 action(3)
 report['options_applied']=get(instance,['MasterVolume','Brightness','MenuMotion'])
 assert report['options_applied']=={'MasterVolume':.65,'Brightness':.95,'MenuMotion':False},report
 report['audio_mix']=get(instance,['PreferenceMix'])
 assert isinstance(report['audio_mix']['PreferenceMix'],dict),report
 shot('Options_Applied')
 props(instance,original)
 action(8)
 action(2)
 props(menu,{'Selected':1});action(1);time.sleep(.8)
 worlds=find(W);assert worlds,'Load did not enter the woods'
 report['loaded_world']=get(worlds[0],['DayNumber','TimeOfDayMinutes','RealSecondsPerDay','ClockPaused'])
 assert report['loaded_world']['DayNumber']==7,report
 assert 1163.4567890123<=report['loaded_world']['TimeOfDayMinutes']<1170,report
 assert report['loaded_world']['RealSecondsPerDay']==1800,report
 report['pending_load']=get(instance,['PendingLoad'])
 assert not report['pending_load']['PendingLoad']
 call('StopPIE',{},APP)
 call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':0}},APP);time.sleep(.4)
 live=find(T)[0];action(4);menu=get(live,['Menu'])['Menu']
 instance=get(menu,['Instance'])['Instance']
 props(instance,{'OptionsSlot':'Evergrove_Options_Validation_20261015'});action(7)
 report['preferences_fresh_session']=get(instance,['MasterVolume','Brightness','MenuMotion'])
 assert report['preferences_fresh_session']==report['options_applied'],report
 props(instance,original);action(8)
 props(menu,{'HasSave':False,'Selected':0});action(1);time.sleep(.8)
 opening=get(instance,['ActiveOpening'])['ActiveOpening']
 assert isinstance(opening,dict)
 props(opening,{'Age':1.0,'RequestedSkip':True});time.sleep(.7)
 opening=get(instance,['ActiveOpening'])['ActiveOpening']
 assert get(opening,['Phase'])['Phase']==1
 props(opening,{'Age':1.0,'RequestedSkip':True});time.sleep(.4)
 worlds=find(W);assert worlds,'New Game did not enter the woods'
 report['new_game']=get(worlds[0],['DayNumber','TimeOfDayMinutes'])
 assert report['new_game']['DayNumber']==1 and 480<=report['new_game']['TimeOfDayMinutes']<490,report
 (OUT/'runtime.json').write_text(json.dumps(report,indent=2))
 print('EVERGROVE_INTRO_RUNTIME_PASSED '+json.dumps(report),flush=True)
finally:
 if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
 call('remove_from_scene',{'actor':probe},SCENE)
 props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':True})
