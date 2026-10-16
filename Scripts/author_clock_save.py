"""Extend existing quick-save with exact clock continuity and legacy compatibility."""
from build_companion_combat import *
WORLD='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
OUT=ROOT/'Saved/ClockSaveAudit';OUT.mkdir(exist_ok=True)
fields=[('HasWorldClock','bool'),('SavedWorldDay','int'),('SavedWorldMinutes','float'),('SavedWorldDayLength','float'),('SavedWorldClockPaused','bool')]
for name,typ in fields:var(SAVE,name,typ)
defaults(SAVE,{'HasWorldClock':False,'SavedWorldDay':1,'SavedWorldMinutes':480,'SavedWorldDayLength':1200,'SavedWorldClockPaused':False})
graph(WORLD,'CaptureWorldClock','''(fn CaptureWorldClock (Snapshot)
 (Class|BPPlayerSave|SetHasWorldClock :self Snapshot :HasWorldClock true)
 (Class|BPPlayerSave|SetSavedWorldDay :self Snapshot :SavedWorldDay (Variables|Default|GetDayNumber))
 (Class|BPPlayerSave|SetSavedWorldMinutes :self Snapshot :SavedWorldMinutes (Variables|Default|GetTimeOfDayMinutes))
 (Class|BPPlayerSave|SetSavedWorldDayLength :self Snapshot :SavedWorldDayLength (Variables|Default|GetRealSecondsPerDay))
 (Class|BPPlayerSave|SetSavedWorldClockPaused :self Snapshot :SavedWorldClockPaused (Variables|Default|GetClockPaused)))''',[('Snapshot',SAVE+'_C',None)])
graph(WORLD,'RestoreWorldClock','''(fn RestoreWorldClock (Snapshot)
 (if (Class|BPPlayerSave|GetHasWorldClock :self Snapshot)
  (Variables|Default|SetDayNumber (Class|BPPlayerSave|GetSavedWorldDay :self Snapshot))
  (Variables|Default|SetTimeOfDayMinutes (Class|BPPlayerSave|GetSavedWorldMinutes :self Snapshot))
  (Variables|Default|SetRealSecondsPerDay (Class|BPPlayerSave|GetSavedWorldDayLength :self Snapshot))
  (Variables|Default|SetClockPaused (Class|BPPlayerSave|GetSavedWorldClockPaused :self Snapshot))
  (CallFunction|AdvanceWorldClock :Delta 0.0)
  (CallFunction|ApplyDayNight)
  (CallFunction|UpdateCamera :Delta 1.0)))''',[('Snapshot',SAVE+'_C',None)])
call('compile_blueprint',{'blueprint':ref(WORLD),'warnings_as_errors':True})
graph(PLAYER,'ValidateWorldClockSnapshot','''(fn ValidateWorldClockSnapshot (Snapshot)
 (if (not (Class|BPPlayerSave|GetHasWorldClock :self Snapshot)) (return true))
 (bind minutes (Class|BPPlayerSave|GetSavedWorldMinutes :self Snapshot))
 (bind length (Class|BPPlayerSave|GetSavedWorldDayLength :self Snapshot))
 (bind worlds (Actor|GetAllActorsOfClass :ActorClass "/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld_C"))
 (return (and (and (and (>= minutes 0.0) (< minutes 1440.0)) (and (> length 0.0) (<= length 31536000.0)))
  (and (>= (Class|BPPlayerSave|GetSavedWorldDay :self Snapshot) 1)
   (> (Utilities|Array|Length worlds) 0)))))''',[('Snapshot',SAVE+'_C',None)],[('Valid','bool',None)])
for function,verb in [('CaptureClockForSave','CaptureWorldClock'),('RestoreClockFromSave','RestoreWorldClock')]:
    graph(PLAYER,function,f'''(fn {function} (Snapshot)
 (for actor (Actor|GetAllActorsOfClass :ActorClass "{WORLD}_C")
  (bind world (Utilities|Casting|CastToBP_WoodlandWorld :Object actor)
   (:then (Class|BPWoodlandWorld|{verb} :self world :Snapshot Snapshot)) (:CastFailed))))''',[('Snapshot',SAVE+'_C',None)])
# Use authored sources because graph readback loses struct output pins.
for name in ['CapturePlayerSave','RestorePlayerSave','ValidatePlayerSave']:
    before=OUT/(name+'_before.dsl')
    if not before.exists():before.write_text(call('read_graph_dsl',{'graph':ref(PLAYER+':'+name)}),encoding='utf-8')
    source=(ROOT/'Saved/CombatAudit'/(name+'.dsl')).read_text(encoding='utf-8')
    if name=='CapturePlayerSave' and '(CallFunction|CaptureClockForSave' not in source:
        assert '(return save)' in source
        source=source.replace('(return save)','(CallFunction|CaptureClockForSave :Snapshot save)\n(return save)',1)
    elif name=='RestorePlayerSave' and '(CallFunction|RestoreClockFromSave' not in source:
        assert '(return true)' in source
        source=source.replace('(return true)','(CallFunction|RestoreClockFromSave :Snapshot Snapshot)\n(return true)',1)
    elif name=='ValidatePlayerSave' and '(CallFunction|ValidateWorldClockSnapshot' not in source:
        assert '(:"Is Valid"' in source
        source=source.replace('(:"Is Valid"','(:"Is Valid"\n (if (not (CallFunction|ValidateWorldClockSnapshot :Snapshot Snapshot)) (return false))',1)
    graph(PLAYER,name,source)
call('compile_blueprint',{'blueprint':ref(PLAYER),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[]},ASSET)
print('EXACT_WORLD_CLOCK_SAVE_AUTHORED',flush=True)
