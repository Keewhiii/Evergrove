import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import quest_bank_mcp as q
BANK=q.BANK;PLAYER=q.PLAYER;P=PLAYER+'_C';call=q.call
_catalog_path = q.ROOT / 'Docs/RepeatableQuestCatalog.json'
if _catalog_path.exists() and any(e.get('objectiveType') in ('Combat', 'Collection') for e in __import__('json').loads(_catalog_path.read_text())):
 raise SystemExit('This one-time migration is superseded by the installed mixed quest bank. Author quests through DT_Quests and their rule assets; see Docs/QuestBank.md.')

ENEMY='/Game/Game/Quests/Objectives/BP_QuestEnemy.BP_QuestEnemy';PICKUP='/Game/Game/Quests/Objectives/BP_QuestPickup.BP_QuestPickup'
f=q.function('CleanupQuestObjectives',[('Player',P,None),('QuestID','name',None)],[])
code='(fn CleanupQuestObjectives (Player QuestID)\n'
for path,cls in [(ENEMY,'BPQuestEnemy'),(PICKUP,'BPQuestPickup')]:
 code+=f''' (bind actors{cls} (Actor|GetAllActorsOfClass :WorldContextObject Player :ActorClass "{path}_C"))
 (for actor{cls} actors{cls}
  (bind typed{cls} (Utilities|Casting|CastTo{path.split('.')[-1]} :Object actor{cls})
   (:then
    (if (and (== (Class|{cls}|GetQuestOwner typed{cls}) Player) (== (Class|{cls}|GetSpawnQuestID typed{cls}) QuestID))
     (Actor|DestroyActor :self typed{cls})))
   (:CastFailed)))
'''
q.write(f,code+' (return))')
q.BANK=PLAYER
f=q.function('SpawnQuestObjectives',[('Player',P,None),('QuestID','name',None),('Kind','name',None),('TargetType','name',None),('Required','int',None)],[('Spawned','int',None)],[('SpawnCount','int',None)])
code='''(fn SpawnQuestObjectives (Player QuestID)
 (Variables|Default|SetSpawnCount 0)
 (bind kind Kind)
 (bind target TargetType)
 (bind required Required)
 (bind location (Transformation|GetActorLocation :self Player))
 (for index (range required)
  (bind offset (Math|Vector|MakeVector :X (+ 350.0 (* index 90.0)) :Y (Math|Random|RandomFloatinRange -180.0 180.0) :Z 0.0))
  (bind transform (Math|Transform|MakeTransform :Location (+ location offset) :Scale (Math|Vector|MakeVector 0.5 0.5 0.5)))
'''
for typ,path,cls in [('Combat',ENEMY,'BPQuestEnemy'),('Collection',PICKUP,'BPQuestPickup')]:
 code+=f'''  (if (== kind (Utilities|String|StringToName "{typ}"))
   (bind spawned{cls} (Game|SpawnActorfromClass :Class "{path}_C" :SpawnTransform transform :CollisionHandlingOverride "AdjustIfPossibleButDontSpawnIfColliding"))
   (Utilities|IsValid spawned{cls}
    (:"Is Valid"
     (Class|{cls}|SetObjectiveTargetType :self spawned{cls} :ObjectiveTargetType target)
     (Class|{cls}|SetSpawnQuestID :self spawned{cls} :SpawnQuestID QuestID)
     (Class|{cls}|SetQuestOwner :self spawned{cls} :QuestOwner Player)
'''
 if typ=='Combat':code+='     (Class|BPQuestEnemy|SetMaximumHealth :self spawnedBPQuestEnemy :MaximumHealth required)\n     (Class|BPQuestEnemy|SetHealth :self spawnedBPQuestEnemy :Health required)\n'
 code+='     (Variables|Default|SetSpawnCount (+ (Variables|Default|GetSpawnCount) 1)))\n    (:"Is Not Valid")))\n'
code+=' )\n (return (Variables|Default|GetSpawnCount)))'
q.write(f,code)
q.BANK=BANK
wrapper='''(fn SpawnQuestObjectives (Player QuestID)
 (bind (kind target required) (CallFunction|GetObjectiveRequirement :QuestID QuestID))
 (bind count (Class|BPPlayer|SpawnQuestObjectives :self Player :Player Player :QuestID QuestID :Kind kind :TargetType target :Required required))
 (return count))'''
q.write({'refPath':BANK+':SpawnQuestObjectives'},wrapper)
# Spawn only on a successful new acceptance, rolling back if there is insufficient space.
code=(q.AUDIT/'TryAcceptQuest_before_spawning.dsl').read_text()
needle='(return true description)'
code=code.replace(needle,'''(bind (kind objectiveTarget required) (CallFunction|GetObjectiveRequirement :QuestID QuestID))
     (if (or (== kind (Utilities|String|StringToName "Combat")) (== kind (Utilities|String|StringToName "Collection")))
      (bind count (CallFunction|SpawnQuestObjectives :Player Player :QuestID QuestID))
      (if (>= count required)
       (return true description)
       (else
        (CallFunction|CleanupQuestObjectives :Player Player :QuestID QuestID)
        (Utilities|Array|RemoveItem (Class|BPPlayer|GetActiveQuestIDs Player) QuestID)
        (Utilities|Map|Remove (Class|BPPlayer|GetQuestProgress Player) (Utilities|String|ToString(Name) QuestID))
        (return false "There isn't enough clear space nearby for this request. Move to an open area and try again.")))
      (else (return true description)))''')
q.write({'refPath':BANK+':TryAcceptQuest'},code)
code=(q.AUDIT/'TryCompleteQuest.dsl').read_text()
needle='(bind reply (CallFunction|GetTurnInReply :QuestID QuestID :AlreadyCompleted false))'
code=code.replace(needle,'(CallFunction|CleanupQuestObjectives :Player Player :QuestID QuestID)\n           '+needle)
q.write({'refPath':BANK+':TryCompleteQuest'},code)
print('Spawn and cleanup saved',call('save_assets',{'asset_paths':[BANK,PLAYER]},'editor_toolset.toolsets.asset.AssetTools'))
