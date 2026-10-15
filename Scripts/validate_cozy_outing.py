"""Isolated introductory quest checks and two in-game art captures."""
from build_cozy_outing import *
TEST='/Game/Tests/World/BP_CozyOutingValidation.BP_CozyOutingValidation'

def author():
    create(TEST,'/Script/Engine.Actor');var(TEST,'Failures','int')
    graph(TEST,'Check','''(fn Check (Condition Label)
 (if Condition (Development|PrintString :InString (Utilities|String|Append "COZY_PASS " Label) :bPrintToScreen false)
 (else (Variables|Default|SetFailures (+ (Variables|Default|GetFailures) 1)) (Development|PrintString :InString (Utilities|String|Append "COZY_FAIL " Label) :bPrintToScreen false))))''',[('Condition','bool',None),('Label','string',None)])
    check=lambda c,l:f'(CallFunction|Check :Condition {c} :Label "{l}")\n'
    code='''(fn Run (Player)
 (bind snapshot (Class|BPPlayer|CapturePlayerSave :self Player))
 (bind bank (Class|BPPlayer|GetQuestBank :self Player))
 (Utilities|Array|Clear (Class|BPPlayer|GetActiveQuestIDs :self Player))
 (Utilities|Array|Clear (Class|BPPlayer|GetCompletedQuestIDs :self Player))
 (Utilities|Map|Clear (Class|BPPlayer|GetQuestProgress :self Player))
 (Utilities|Map|Clear (Class|BPPlayer|GetInventoryItems :self Player))
 (Class|BPPlayer|SetGold :self Player :Gold 0)
'''
    code+=check(f'(== (Utilities|Array|Length (Actor|GetAllActorsOfClass :ActorClass "{COZY}_C")) 1)','One dressing actor, no duplicates')
    code+=f'''(bind (locked lockedReply) (Class|BPQuestBank|TryAcceptQuest :self bank :Player Player :GiverName "Luna" :QuestID "{FIRST}"))
'''+check('(not locked)','Original delivery remains first')
    code+='(Utilities|Array|AddUnique (Class|BPPlayer|GetCompletedQuestIDs :self Player) "0_Delivery_001")\n'
    code+=f'''(bind (early earlyReply) (Class|BPQuestBank|TryAcceptQuest :self bank :Player Player :GiverName "Luna" :QuestID "{SECOND}"))
'''+check('(not early)','Patrol locked until tea is complete')
    code+=f'''(bind (accepted quest reply) (Class|BPQuestBank|RequestQuest :self bank :Player Player :GiverName "Luna"))
'''+check(f'(and accepted (== quest (Utilities|Name|MakeLiteralName "{FIRST}")))','Luna offers tea before random commissions')
    code+=f'''(bind (premature prematureReply) (Class|BPQuestBank|TryCompleteQuest :self bank :Player Player :TargetName "Luna" :QuestID "{FIRST}"))
'''+check('(not premature)','Tea requires actual gathering')
    code+='''(for actor (Actor|GetAllActorsOfClass :ActorClass "/Game/Game/Quests/Objectives/BP_QuestPickup.BP_QuestPickup_C")
 (bind pickup (Utilities|Casting|CastToBP_QuestPickup :Object actor)
 (:then (bind collected (Class|BPQuestPickup|CollectForPlayer :self pickup :Player Player))) (:CastFailed)))
'''
    code+=f'''(bind (wrong wrongReply) (Class|BPQuestBank|TryCompleteQuest :self bank :Player Player :TargetName "Rein" :QuestID "{FIRST}"))
'''+check('(not wrong)','Tea turns in only to Luna')
    code+=f'''(bind (teaDone teaReply) (Class|BPQuestBank|TryCompleteQuest :self bank :Player Player :TargetName "Luna" :QuestID "{FIRST}"))
'''+check('(and teaDone (== (Class|BPPlayer|GetGold :self Player) 20))','Tea pays exactly 20 gold')
    code+=f'''(bind (patrol patrolID patrolReply) (Class|BPQuestBank|RequestQuest :self bank :Player Player :GiverName "Luna"))
'''+check(f'(and patrol (== patrolID (Utilities|Name|MakeLiteralName "{SECOND}")))','Luna offers the patrol next')
    code+='''(for actor (Actor|GetAllActorsOfClass :ActorClass "/Game/Game/Quests/Objectives/BP_QuestEnemy.BP_QuestEnemy_C")
 (bind enemy (Utilities|Casting|CastToBP_QuestEnemy :Object actor)
 (:then (bind killed (Class|BPQuestEnemy|TakeQuestDamage :self enemy :Player Player :Damage 100.0))) (:CastFailed)))
'''
    code+=f'''(bind (done finalReply) (Class|BPQuestBank|TryCompleteQuest :self bank :Player Player :TargetName "Luna" :QuestID "{SECOND}"))
'''+check('(and done (== (Class|BPPlayer|GetGold :self Player) 60))','Patrol pays 40 more gold')
    code+=f'''(bind (duplicate duplicateReply) (Class|BPQuestBank|TryCompleteQuest :self bank :Player Player :TargetName "Luna" :QuestID "{SECOND}"))
'''+check('(and (not duplicate) (== (Class|BPPlayer|GetGold :self Player) 60))','No duplicate rewards')
    code+=f'''(bind (replay replayReply) (Class|BPQuestBank|TryAcceptQuest :self bank :Player Player :GiverName "Luna" :QuestID "{FIRST}"))
'''+check('(not replay)','Authored outing is one time')
    code+='''(bind restored (Class|BPPlayer|RestorePlayerSave :self Player :Snapshot snapshot))
 (Development|PrintString :InString (Utilities|String|Append "COZY_FINAL_FAILURES=" (Utilities|String|ToString(Integer) (Variables|Default|GetFailures))) :bPrintToScreen false))'''
    graph(TEST,'Run',code,[('Player',PLAYER+'_C',None)])
    graph(TEST,'EventGraph','''(event EventBeginPlay
 (Utilities|FlowControl|Delay 4.0)
 (bind player (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0))
 (:then (CallFunction|Run :Player player)
 (Transformation|SetActorLocation :self player :NewLocation (Math|Vector|MakeVector 0.0 100.0 100.0) :bTeleport true)
 (Utilities|FlowControl|Delay 2.0)
 (Development|ExecuteConsoleCommand :Command "Shot showui" :SpecificPlayer (Game|GetPlayerController 0))
 (Transformation|SetActorLocation :self player :NewLocation (Math|Vector|MakeVector 1800.0 0.0 100.0) :bTeleport true)
 (Utilities|FlowControl|Delay 3.0)
 (Development|ExecuteConsoleCommand :Command "Shot showui" :SpecificPlayer (Game|GetPlayerController 0))) (:CastFailed)))''')
    call('save_assets',{'asset_paths':[TEST]},ASSET)

if __name__=='__main__':author()
