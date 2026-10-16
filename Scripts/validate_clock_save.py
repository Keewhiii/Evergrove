"""Exercise real disk quick-save/load and a separate fresh PIE session."""
from build_companion_combat import *
import time
T='/Game/Tests/World/BP_ClockSaveValidation.BP_ClockSaveValidation'
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools'
OUT=ROOT/'Saved/ClockSaveAudit';OUT.mkdir(exist_ok=True)
SLOT='AdventureRPG_ClockContinuityValidation_20261015'
create(T,'/Script/Engine.Actor')
fields=[('Player',PLAYER+'_C'),('World',W+'_C'),('Snapshot',SAVE+'_C'),('Requested','bool'),('Mode','int'),('Done','bool'),('Failures','int'),('OriginalSlot','string'),('ExpectedMinutes','float'),('ExpectedDay','int'),('ExpectedRate','float'),('ObservedMinutes','float'),('ObservedDay','int'),('ObservedRate','float'),('ObservedPaused','bool')]
for n,t in fields:var(T,n,t)
for n in ['Requested','Mode']:
    call('set_variable_instance_editable',{'blueprint':ref(T),'variable_name':n,'instance_editable':True})
def v(name):return '(Variables|Default|Get'+name+')'
P=v('Player');WORLD=v('World');SNAP=v('Snapshot')
def world_get(name):return '(Class|BPWoodlandWorld|Get'+name+' :self '+WORLD+')'
def world_set(name,value):return '(Class|BPWoodlandWorld|Set'+name+' :self '+WORLD+' :'+name+' '+str(value)+')\n'
def check(condition,label):return '(CallFunction|Check :Condition '+condition+' :Message "'+label+'")\n'
graph(T,'Check','''(fn Check (Condition Message)
 (if (not Condition)
  (Variables|Default|SetFailures (+ (Variables|Default|GetFailures) 1))
  (Development|PrintString :InString Message :bPrintToScreen false :bPrintToLog true)))''',[('Condition','bool',None),('Message','string',None)])
graph(T,'InitializeReferences',f'''(fn InitializeReferences ()
 (for actor (Actor|GetAllActorsOfClass :ActorClass "{W}_C")
  (bind world (Utilities|Casting|CastToBP_WoodlandWorld :Object actor)
   (:then (Variables|Default|SetWorld world)) (:CastFailed)))
 (bind player (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0))
  (:then (Variables|Default|SetPlayer player)) (:CastFailed)))''')
graph(T,'ReadTestDiskSnapshot',f'''(fn ReadTestDiskSnapshot ()
 (bind disk (Utilities|Casting|CastToBP_PlayerSave :Object (SaveGame|LoadGameFromSlot :SlotName "{SLOT}" :UserIndex 0))
  (:then (Variables|Default|SetSnapshot disk))
  (:CastFailed (CallFunction|Check :Condition false :Message "CLOCK_FAIL: disk snapshot class"))))''')
verify='(fn VerifyLoadedClock ()\n'
verify+=check('(== '+world_get('TimeOfDayMinutes')+' '+v('ExpectedMinutes')+')','CLOCK_FAIL: fractional minutes changed')
verify+=check('(== '+world_get('DayNumber')+' '+v('ExpectedDay')+')','CLOCK_FAIL: day changed')
verify+=check('(== '+world_get('RealSecondsPerDay')+' '+v('ExpectedRate')+')','CLOCK_FAIL: cycle speed changed')
verify+=check('(not '+world_get('ClockPaused')+')','CLOCK_FAIL: running clock did not resume')
verify+=check(world_get('IsNight'),'CLOCK_FAIL: lighting not restored immediately')
verify+=check('(== '+world_get('NightLightFactor')+' 1.0)','CLOCK_FAIL: lantern state not restored immediately')
verify+='(Variables|Default|SetObservedMinutes '+world_get('TimeOfDayMinutes')+')\n(Variables|Default|SetObservedDay '+world_get('DayNumber')+')\n(Variables|Default|SetObservedRate '+world_get('RealSecondsPerDay')+')\n(Variables|Default|SetObservedPaused '+world_get('ClockPaused')+'))'
graph(T,'VerifyLoadedClock',verify)
prepare='(Variables|Default|SetOriginalSlot (Class|BPPlayer|GetSaveSlotName :self '+P+'))\n(Class|BPPlayer|SetSaveSlotName :self '+P+' :SaveSlotName "'+SLOT+'")\n'
restore_slot='(Class|BPPlayer|SetSaveSlotName :self '+P+' :SaveSlotName '+v('OriginalSlot')+')\n(Variables|Default|SetDone true)\n'
code='(fn RunRoundTrip ()\n'+prepare
code+=world_set('DayNumber',v('ExpectedDay'))+world_set('TimeOfDayMinutes',v('ExpectedMinutes'))+world_set('RealSecondsPerDay',v('ExpectedRate'))+world_set('ClockPaused','false')
code+='(Class|BPPlayer|SetGold :self '+P+' :Gold 42)\n'
code+='(bind saved (Class|BPPlayer|SaveProgress :self '+P+'))\n'+check('saved','CLOCK_FAIL: disk save failed')
code+='(CallFunction|ReadTestDiskSnapshot)\n'
code+=check('(Class|BPPlayerSave|GetHasWorldClock :self '+SNAP+')','CLOCK_FAIL: snapshot has no clock')
code+=check('(== (Class|BPPlayerSave|GetSavedWorldMinutes :self '+SNAP+') '+v('ExpectedMinutes')+')','CLOCK_FAIL: disk changed clock precision')
code+=world_set('DayNumber',99)+world_set('TimeOfDayMinutes',120.0)+world_set('RealSecondsPerDay',600.0)+world_set('ClockPaused','true')
code+='(Class|BPPlayer|SetGold :self '+P+' :Gold 99)\n(bind loaded (Class|BPPlayer|LoadProgress :self '+P+'))\n'
code+=check('loaded','CLOCK_FAIL: disk load failed')+'(CallFunction|VerifyLoadedClock)\n'
code+=check('(== (Class|BPPlayer|GetGold :self '+P+') 42)','CLOCK_FAIL: player state did not restore')
code+='(Class|BPWoodlandWorld|AdvanceWorldClock :self '+WORLD+' :Delta 0.5)\n'
code+=check('(> '+world_get('TimeOfDayMinutes')+' '+v('ExpectedMinutes')+')','CLOCK_FAIL: time does not advance after load')
# Verify paused time, exact near-midnight restoration, and rollover using an in-memory snapshot.
code+=world_set('ClockPaused','true')+world_set('DayNumber',v('ExpectedDay'))+world_set('TimeOfDayMinutes',1439.75)
code+='(bind midnight (Class|BPPlayer|CapturePlayerSave :self '+P+'))\n'
code+=world_set('DayNumber',1)+world_set('TimeOfDayMinutes',0.0)+world_set('ClockPaused','false')
code+='(bind pausedLoaded (Class|BPPlayer|RestorePlayerSave :self '+P+' :Snapshot midnight))\n'+check('pausedLoaded','CLOCK_FAIL: paused snapshot load failed')
code+=check(world_get('ClockPaused'),'CLOCK_FAIL: pause state lost')
code+='(Class|BPWoodlandWorld|AdvanceWorldClock :self '+WORLD+' :Delta 0.5)\n'
code+=check('(== '+world_get('TimeOfDayMinutes')+' 1439.75)','CLOCK_FAIL: paused clock advanced')
code+=world_set('ClockPaused','false')+'(Class|BPWoodlandWorld|AdvanceWorldClock :self '+WORLD+' :Delta 0.5)\n'
code+=check('(== '+world_get('DayNumber')+' (+ '+v('ExpectedDay')+' 1))','CLOCK_FAIL: midnight day rollover')
code+=check('(and (> '+world_get('TimeOfDayMinutes')+' 0.14999) (< '+world_get('TimeOfDayMinutes')+' 0.15001))','CLOCK_FAIL: midnight fractional rollover')
# Legacy snapshots load normally without inventing or resetting a clock.
code+='(Class|BPPlayerSave|SetHasWorldClock :self '+SNAP+' :HasWorldClock false)\n'
code+=world_set('ClockPaused','true')+world_set('DayNumber',88)+world_set('TimeOfDayMinutes',1010.0)
code+='(bind legacyLoaded (Class|BPPlayer|RestorePlayerSave :self '+P+' :Snapshot '+SNAP+'))\n'+check('legacyLoaded','CLOCK_FAIL: legacy compatibility')
code+=check('(and (== '+world_get('TimeOfDayMinutes')+' 1010.0) (== '+world_get('DayNumber')+' 88))','CLOCK_FAIL: legacy load reset the clock')
# Malformed time data must reject before changing player or clock state.
code+='(Class|BPPlayerSave|SetHasWorldClock :self '+SNAP+' :HasWorldClock true)\n(Class|BPPlayerSave|SetSavedWorldMinutes :self '+SNAP+' :SavedWorldMinutes 1440.0)\n(Class|BPPlayerSave|SetGold :self '+SNAP+' :Gold 9999)\n(Class|BPPlayer|SetGold :self '+P+' :Gold 222)\n'
code+='(bind invalidLoaded (Class|BPPlayer|RestorePlayerSave :self '+P+' :Snapshot '+SNAP+'))\n'+check('(not invalidLoaded)','CLOCK_FAIL: invalid minutes accepted')
code+=check('(and (== (Class|BPPlayer|GetGold :self '+P+') 222) (== '+world_get('TimeOfDayMinutes')+' 1010.0))','CLOCK_FAIL: rejected load partially mutated state')
code+='(Class|BPPlayerSave|SetSavedWorldMinutes :self '+SNAP+' :SavedWorldMinutes '+v('ExpectedMinutes')+')\n(Class|BPPlayerSave|SetSavedWorldDay :self '+SNAP+' :SavedWorldDay 0)\n'
code+='(bind invalidDay (Class|BPPlayer|ValidatePlayerSave :self '+P+' :Snapshot '+SNAP+'))\n'+check('(not invalidDay)','CLOCK_FAIL: invalid day accepted')
code+='(Class|BPPlayerSave|SetSavedWorldDay :self '+SNAP+' :SavedWorldDay 7)\n(Class|BPPlayerSave|SetSavedWorldDayLength :self '+SNAP+' :SavedWorldDayLength 0.0)\n'
code+='(bind invalidRate (Class|BPPlayer|ValidatePlayerSave :self '+P+' :Snapshot '+SNAP+'))\n'+check('(not invalidRate)','CLOCK_FAIL: invalid rate accepted')
code+=restore_slot+')'
graph(T,'RunRoundTrip',code)
fresh='(fn RunFreshSession ()\n'+prepare
fresh+='(bind loaded (Class|BPPlayer|LoadProgress :self '+P+'))\n'+check('loaded','CLOCK_FAIL: fresh session disk load')+'(CallFunction|VerifyLoadedClock)\n'
fresh+=check('(== (Class|BPPlayer|GetGold :self '+P+') 42)','CLOCK_FAIL: fresh player restore')
fresh+=restore_slot+')'
graph(T,'RunFreshSession',fresh)
graph(T,'EventGraph','''(event EventTick (DeltaSeconds)
 (if (Variables|Default|GetRequested)
  (Variables|Default|SetRequested false)
  (CallFunction|InitializeReferences)
  (if (== (Variables|Default|GetMode) 0) (CallFunction|RunRoundTrip) (else (CallFunction|RunFreshSession)))))''')
defaults(T,{'ExpectedDay':7,'ExpectedMinutes':1163.4567890123,'ExpectedRate':1800,'Failures':0,'Done':False,'Requested':False})
call('save_assets',{'asset_paths':[T]},ASSET)
probe=call('add_to_scene_from_asset',{'asset_path':T.split('.')[0],'name':'ClockSave_TemporaryProbe','xform':{},'snap_to_ground':False},SCENE)
call('set_label',{'actor':probe,'label':'ClockSave_TemporaryProbe'},ACT)
report={}
def get(o,keys):return json.loads(call('get_properties',{'instance':o,'properties':keys},OBJ))
def props(o,values):return call('set_properties',{'instance':o,'values':json.dumps(values)},OBJ)
try:
    props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':False})
    for mode,label in [(0,'disk_round_trip'),(1,'fresh_session')]:
        call('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':0}},APP)
        time.sleep(.4)
        live=call('find_actors',{'name':'ClockSave_TemporaryProbe','tag':'','collision_channels':[]},SCENE)[0]
        props(live,{'Mode':mode,'Requested':True})
        deadline=time.monotonic()+15
        while time.monotonic()<deadline:
            result=get(live,['Done','Failures','ObservedMinutes','ObservedDay','ObservedRate','ObservedPaused'])
            if result['Done']:break
            time.sleep(.1)
        assert result['Done'] and result['Failures']==0,result
        assert result['ObservedMinutes']==1163.4567890123,result
        report[label]=result
        if mode==1:
            world=call('find_actors',{'name':'','tag':'','collision_channels':[],'actor_type':ref(W+'_C')},SCENE)[0]
            a=get(world,['TimeOfDayMinutes'])['TimeOfDayMinutes'];time.sleep(.3)
            b=get(world,['TimeOfDayMinutes'])['TimeOfDayMinutes'];assert b>a,(a,b)
            report['resumed_time_samples']=[a,b]
        call('StopPIE',{},APP)
    (OUT/'runtime.json').write_text(json.dumps(report,indent=2))
    print('EXACT_CLOCK_DISK_AND_FRESH_SESSION_PASSED '+json.dumps(report),flush=True)
finally:
    if call('IsPIERunning',{},APP):call('StopPIE',{},APP)
    call('remove_from_scene',{'actor':probe},SCENE)
    props(ref('/Script/UnrealEd.Default__EditorPerformanceSettings'),{'bThrottleCPUWhenNotForeground':True})
