"""Author isolated PIE checks for encounters, party summons and existing saves."""
from build_companion_combat import *

TEST = '/Game/Tests/Combat/BP_PartyCombatValidation.BP_PartyCombatValidation'
D = 'D'
get = lambda n: f'(Class|BPCompanionCombat|Get{n} :self D)'
setv = lambda n, value: f'(Class|BPCompanionCombat|Set{n} :self D :{n} {value})'
act = lambda n, args='': f'(Class|BPCompanionCombat|{n} :self D {args})'


def author():
    create(TEST, '/Script/Engine.Actor')
    var(TEST, 'Failures', 'int')
    var(TEST, 'LiveCount', 'int')
    var(TEST, 'FirstFollower', BEAST+'_C')
    graph(TEST, 'Check', '''(fn Check (Condition Label)
    (if Condition (Development|PrintString :InString (Utilities|String|Append "PARTY_PASS " Label) :bPrintToScreen false)
     (else (Variables|Default|SetFailures (+ (Variables|Default|GetFailures) 1))
      (Development|PrintString :InString (Utilities|String|Append "PARTY_FAIL " Label) :bPrintToScreen false))))''',
          [('Condition','bool',None), ('Label','string',None)])
    graph(TEST, 'CountSummons', f'''(fn CountSummons (D)
    (Variables|Default|SetLiveCount 0)
    (for actor (Actor|GetAllActorsOfClass :ActorClass "{BEAST}_C")
     (bind beast (Utilities|Casting|CastToBP_Beast :Object actor)
      (:then (if (Class|BPBeast|GetIsCompanion :self beast)
       (Variables|Default|SetLiveCount (+ (Variables|Default|GetLiveCount) 1)))) (:CastFailed)))
    (return (Variables|Default|GetLiveCount)))''', [('D',DIRECTOR+'_C',None)], [('Count','int',None)])

    def check(condition, label):
        return f'(CallFunction|Check :Condition {condition} :Label "{label}")\n'

    count = '(CallFunction|CountSummons :D D)'
    now = '(Utilities|Time|GetGameTimeinSeconds)'
    code = f'''(fn RunChecks (D)
    (bind player {get('Player')})
    (bind original (Class|BPPlayer|CapturePlayerSave :self player))
    (bind originalSlot (Class|BPPlayer|GetSaveSlotName :self player))
    (Utilities|Time|ClearTimerbyFunctionName :Object D :FunctionName "CombatStep")
    {act('ClearParty')}
    (Utilities|Array|Clear {get('Roster')})
    (Utilities|Array|Add {get('Roster')} "Mossling")
    (Utilities|Array|Add {get('Roster')} "Rivercub")
    (Utilities|Array|Add {get('Roster')} "Moonmoth")
    {setv('ActiveIndex','0')}{setv('InCombat','false')}
    {setv('CompanionHealth','60.0')}{setv('RetreatUntil','0.0')}
    {act('SyncParty')}
    ''' + check(f'(== {count} 1)', 'One overworld follower')
    code += f'''(Variables|Default|SetFirstFollower {get('Companion')})
    {setv('SwitchReadyAt','0.0')}{act('SummonSlot', ':Index 2')}
    ''' + check(f'(and (== {count} 1) (== {get("ActiveIndex")} 2))', 'Switching follower preserves exactly one summon')
    code += check(f'(== (Class|BPBeast|GetBeastID :self {get("Companion")}) "Moonmoth")', 'Selected overworld species follows')
    code += check(f'(not {act("Valid", ":Object (Variables|Default|GetFirstFollower)")})', 'Previous follower actor is removed')
    code += act('SummonSlot', ':Index 3') + check(f'(== {get("ActiveIndex")} 2)', 'Empty slot does not change follower')
    code += f'''(bind origin (Transformation|GetActorLocation :self player))
    (bind enemy (Game|SpawnActorfromClass :Class "{ENEMY}_C"
     :SpawnTransform (Math|Transform|MakeTransform :Location (+ origin (Math|Vector|MakeVector 600.0 0.0 0.0))) :CollisionHandlingOverride "AlwaysSpawn"))
    (Class|BPQuestEnemy|SetMaximumHealth :self enemy :MaximumHealth 100.0)
    (Class|BPQuestEnemy|SetHealth :self enemy :Health 100.0)
    {act('StepPartyBeast', f':Beast {get("Companion")} :Index 2')}
    ''' + check('(== (Class|BPQuestEnemy|GetHealth :self enemy) 100.0)', 'Follower does not attack while exploring')
    code += act('RefreshEncounter') + act('SyncParty')
    code += check(get('InCombat'), 'Nearby live enemy enters combat')
    code += check(f'(== {count} 3)', 'All three tamed beasts are summoned')
    code += act('ReleaseActive') + check(f'(== (Utilities|Array|Length {get("Roster")} ) 3)', 'Release is blocked during combat')
    for i, species in enumerate(['Mossling','Rivercub','Moonmoth']):
        code += f'(bind friend{i} (Utilities|Array|Get(acopy) {get("PartyActors")} {i}))\n'
        code += check(f'(== (Class|BPBeast|GetBeastID :self friend{i}) "{species}")', f'Party slot {i+1} has the correct species')
        code += f'''(Transformation|SetActorLocation :self friend{i} :NewLocation (Transformation|GetActorLocation :self enemy) :bTeleport true)
        (Class|BPBeast|SetPartyAttackReadyAt :self friend{i} :PartyAttackReadyAt 0.0)
        {act('StepPartyBeast',f':Beast friend{i} :Index {i}')}\n'''
    code += check('(== (Class|BPQuestEnemy|GetHealth :self enemy) 97.0)', 'Every summoned beast deals damage')
    for i in range(3): code += act('StepPartyBeast', f':Beast friend{i} :Index {i}')
    code += check('(== (Class|BPQuestEnemy|GetHealth :self enemy) 97.0)', 'Per-beast attack cooldowns prevent repeat hits')
    code += f'''(bind bank (Class|BPPlayer|GetQuestBank :self player))
    (Utilities|Array|AddUnique (Class|BPPlayer|GetActiveQuestIDs :self player) "RQ_1Star_015")
    (Utilities|Map|Add (Class|BPPlayer|GetQuestProgress :self player) "RQ_1Star_015" 0)
    (bind (kind target required) (Class|BPQuestBank|GetObjectiveRequirement :self bank :QuestID "RQ_1Star_015"))
    (Class|BPQuestEnemy|SetObjectiveTargetType :self enemy :ObjectiveTargetType target)
    (Class|BPQuestEnemy|SetHealth :self enemy :Health 3.0)
    '''
    for i in range(3):
        code += f'(Class|BPBeast|SetPartyAttackReadyAt :self friend{i} :PartyAttackReadyAt 0.0)\n'
        code += act('StepPartyBeast', f':Beast friend{i} :Index {i}')
    code += '''(bind (progress foundProgress) (Utilities|Map|Find (Class|BPPlayer|GetQuestProgress :self player) "RQ_1Star_015"))\n'''
    code += check('(== progress 1)', 'Party kill credits the player quest exactly once')
    code += act('RefreshEncounter') + check(get('InCombat'), 'Combat grace period avoids immediate flicker')
    code += setv('LastThreatAt', f'(- {now} 5.0)') + act('RefreshEncounter') + act('SyncParty')
    code += check(f'(not {get("InCombat")})', 'Combat ends after threats are gone')
    code += check(f'(and (== {count} 1) (== {get("ActiveIndex")} 2))', 'Combat exit restores the selected single follower')
    code += setv('InCombat','true') + act('SyncParty') + setv('HurtReadyAt','0.0') + act('Hurt', ':Amount 100.0 :HitCompanion true') + act('SyncParty')
    code += check(f'(and (== {count} 0) (== {get("CompanionHealth")} 0.0))', 'Knockout retreats all companions sharing party health')
    code += setv('SwitchReadyAt','0.0') + act('SummonSlot', ':Index 0')
    code += check(f'(== {count} 0)', 'Follower switching cannot bypass recovery')
    code += setv('RetreatUntil','0.001') + setv('LastThreatAt',now) + act('CombatStep')
    code += check(f'(and (== {count} 3) (== {get("CompanionHealth")} 60.0))', 'Recovered companions all return during combat')
    code += setv('PlayerHealth','50.0') + setv('CompanionHealth','20.0') + setv('HealReadyAt','0.0') + act('Heal')
    code += check(f'(and (== {get("PlayerHealth")} 85.0) (== {get("CompanionHealth")} 45.0))', 'Healing retains player and shared party amounts')
    code += act('Heal') + check(f'(== {get("PlayerHealth")} 85.0)', 'Heal cooldown is retained')
    code += setv('InCombat','false') + act('SyncParty') + setv('SwitchReadyAt','0.0') + act('SummonSlot',':Index 2')
    code += setv('PlayerHealth','71.0') + setv('CompanionHealth','39.0')
    code += '''(bind snapshot (Class|BPPlayer|CapturePlayerSave :self player))
    (bind validSave (Class|BPPlayer|ValidatePlayerSave :self player :Snapshot snapshot))\n'''
    code += check('validSave', 'Existing save schema accepts party state')
    code += '''(Class|BPPlayer|SetSaveSlotName :self player :SaveSlotName "AdventureRPG_PartyValidation_20261014")
    (bind diskSaved (Class|BPPlayer|SaveProgress :self player))\n'''
    code += check('diskSaved', 'Party state saves to isolated test slot')
    code += setv('PlayerHealth','10.0') + setv('InCombat','true') + act('SyncParty')
    code += '''(bind loaded (Class|BPPlayer|LoadProgress :self player))\n'''
    code += check(f'(and loaded (and (== {count} 1) (not {get("InCombat")})))', 'Load clears battle-only summons and resumes exploration')
    code += check(f'(and (== {get("PlayerHealth")} 71.0) (and (== {get("CompanionHealth")} 39.0) (== {get("ActiveIndex")} 2)))', 'Load retains health and selected follower')
    code += '''(bind restoredAgain (Class|BPPlayer|RestorePlayerSave :self player :Snapshot snapshot))\n'''
    code += check(f'(and restoredAgain (== {count} 1))', 'Repeated restore does not duplicate summons')
    code += setv('HurtReadyAt','0.0') + act('Hurt',':Amount 200.0 :HitCompanion false') + act('SyncParty')
    code += check(f'(and (== {get("PlayerHealth")} 100.0) (== {count} 1))', 'Gentle player defeat returns safely without summon leaks')
    code += '''(SaveGame|DeleteGameinSlot :SlotName "AdventureRPG_PartyValidation_20261014" :UserIndex 0)
    (bind reset (Class|BPPlayer|RestorePlayerSave :self player :Snapshot original))
    (Class|BPPlayer|SetSaveSlotName :self player :SaveSlotName originalSlot)
    (Utilities|Time|SetTimerbyFunctionName :Object D :FunctionName "CombatStep" :Time 0.2 :bLooping true)
    (Development|PrintString :InString (Utilities|String|Append "PARTY_FAILURES=" (Utilities|String|ToString(Integer) (Variables|Default|GetFailures))) :bPrintToScreen false))'''
    if '--enemy-only' not in sys.argv:
        graph(TEST,'RunChecks',code,[('D',DIRECTOR+'_C',None)])
    enemy_checks = f'''(fn RunEnemyChecks (D)
    (bind player {get('Player')})
    (bind original (Class|BPPlayer|CapturePlayerSave :self player))
    (Utilities|Time|ClearTimerbyFunctionName :Object D :FunctionName "CombatStep")
    {act('ClearParty')}
    (Utilities|Array|Clear {get('Roster')})
    (Utilities|Array|Add {get('Roster')} "Mossling")
    (Utilities|Array|Add {get('Roster')} "Rivercub")
    (Utilities|Array|Add {get('Roster')} "Moonmoth")
    {setv('ActiveIndex','2')}{setv('InCombat','true')}
    {setv('CompanionHealth','60.0')}{setv('PlayerHealth','100.0')}{setv('RetreatUntil','0.0')}
    {act('SyncParty')}
    (bind origin (Transformation|GetActorLocation :self player))
    (bind enemy (Game|SpawnActorfromClass :Class "{ENEMY}_C"
     :SpawnTransform (Math|Transform|MakeTransform :Location (+ origin (Math|Vector|MakeVector 400.0 0.0 0.0))) :CollisionHandlingOverride "AlwaysSpawn"))
    (bind secondary (Utilities|Array|Get(acopy) {get('PartyActors')} 0))
    (Transformation|SetActorLocation :self secondary :NewLocation (Transformation|GetActorLocation :self enemy) :bTeleport true)
    {act('EnemyStep', ':Enemy enemy')}
    ''' + check('(Class|BPQuestEnemy|GetWindingUp :self enemy)', 'Enemy winds up against a secondary party member')
    enemy_checks += f'''(Class|BPQuestEnemy|SetAttackAt :self enemy :AttackAt 0.0)
    {setv('HurtReadyAt','0.0')}{act('EnemyStep', ':Enemy enemy')}
    ''' + check(f'(and (== {get("CompanionHealth")} 50.0) (== {get("PlayerHealth")} 100.0))', 'Enemy can damage a secondary summon while player is distant')
    enemy_checks += setv('InCombat','false') + '(Class|BPQuestEnemy|SetAttackAt :self enemy :AttackAt 0.0)' + act('EnemyStep', ':Enemy enemy')
    enemy_checks += check(f'(and (not (Class|BPQuestEnemy|GetWindingUp :self enemy)) (== {get("CompanionHealth")} 50.0))', 'Enemies do not attack while encounter state is inactive')
    enemy_checks += '''(Actor|DestroyActor :self enemy)
    (bind restored (Class|BPPlayer|RestorePlayerSave :self player :Snapshot original))
    (Utilities|Time|SetTimerbyFunctionName :Object D :FunctionName "CombatStep" :Time 0.2 :bLooping true))'''
    graph(TEST,'RunEnemyChecks',enemy_checks,[('D',DIRECTOR+'_C',None)])
    graph(TEST,'EventGraph',f'''(event EventBeginPlay
    (Utilities|FlowControl|Delay 1.0)
    (for actor (Actor|GetAllActorsOfClass :ActorClass "{DIRECTOR}_C")
     (bind director (Utilities|Casting|CastToBP_CompanionCombat :Object actor)
      (:then (CallFunction|RunChecks :D director) (CallFunction|RunEnemyChecks :D director)) (:CastFailed)))
    (Development|PrintString :InString (Utilities|String|Append "PARTY_FINAL_FAILURES=" (Utilities|String|ToString(Integer) (Variables|Default|GetFailures))) :bPrintToScreen false))''')
    print('Saved party checks:',call('save_assets',{'asset_paths':[TEST]},ASSET))


if __name__ == '__main__': author()
