import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import quest_bank_mcp as q
BANK=q.BANK;PLAYER=q.PLAYER;P=PLAYER+'_C';call=q.call
W='/Game/Game/Characters/NPCs/WBP_Dialogue.WBP_Dialogue';NPC='/Game/Game/Characters/NPCs/BP_Npc.BP_Npc';PICKUP='/Game/Game/Quests/Objectives/BP_QuestPickup.BP_QuestPickup'
if 'InventoryItems' not in call('list_variables',{'blueprint':{'refPath':PLAYER}}):call('add_variable',{'blueprint':{'refPath':PLAYER},'name':'InventoryItems','type_name':'int','container_type':'MAP'})
call('compile_blueprint',{'blueprint':{'refPath':PLAYER},'warnings_as_errors':True})
f=q.function('RecordCollectedItems',[('Player',P,None),('ItemType','name',None),('Amount','int',None)],[('Added','bool',None)])
q.write(f,'''(fn RecordCollectedItems (Player ItemType Amount)
 (Utilities|IsValid Player
  (:"Is Valid"
   (if (and (> Amount 0) (!= ItemType (Utilities|String|StringToName "None")))
    (bind (existing found) (Utilities|Map|Find (Class|BPPlayer|GetInventoryItems Player) (Utilities|String|ToString(Name) ItemType)))
    (Utilities|Map|Add (Class|BPPlayer|GetInventoryItems Player) (Utilities|String|ToString(Name) ItemType) (+ existing Amount))
    (bind updated (CallFunction|ReportObjectiveProgress :Player Player :Kind "Collection" :TargetType ItemType :Amount Amount))
    (return true)
    (else (return false))))
  (:"Is Not Valid" (return false))))''')
q.write({'refPath':BANK+':IsQuestObjectiveReady'},'''(fn IsQuestObjectiveReady (Player QuestID)
 (Utilities|IsValid Player
  (:"Is Valid"
   (bind (kind target required) (CallFunction|GetObjectiveRequirement :QuestID QuestID))
   (if (== kind (Utilities|String|StringToName "Collection"))
    (bind (quantity exists) (Utilities|Map|Find (Class|BPPlayer|GetInventoryItems Player) (Utilities|String|ToString(Name) target)))
    (return (and exists (>= quantity required)))
    (elif (== kind (Utilities|String|StringToName "Combat"))
     (bind (progress found) (Utilities|Map|Find (Class|BPPlayer|GetQuestProgress Player) (Utilities|String|ToString(Name) QuestID)))
     (return (and found (>= progress required)))
     (else (return (or (== kind (Utilities|String|StringToName "Delivery")) (== kind (Utilities|String|StringToName "None"))))))))
  (:"Is Not Valid" (return false))))''')
code=(q.AUDIT/'TryCompleteQuest.dsl').read_text()
needle='(Utilities|Array|RemoveItem (Class|BPPlayer|GetActiveQuestIDs Player) QuestID)'
code=code.replace(needle,'''(bind (kind itemType required) (CallFunction|GetObjectiveRequirement :QuestID QuestID))
           (if (== kind (Utilities|String|StringToName "Collection"))
            (bind (quantity exists) (Utilities|Map|Find (Class|BPPlayer|GetInventoryItems Player) (Utilities|String|ToString(Name) itemType)))
            (Utilities|Map|Add (Class|BPPlayer|GetInventoryItems Player) (Utilities|String|ToString(Name) itemType) (- quantity required)))
           '''+needle)
if code.count('(bind (kind itemType required) (CallFunction|GetObjectiveRequirement :QuestID QuestID))') > 1:
 raise RuntimeError('This migration has already been applied; do not apply item consumption twice.')
q.write({'refPath':BANK+':TryCompleteQuest'},code)
f=q.function('TurnInQuests',[('Player',P,None),('NPCID','name',None)],[('CompletedCount','int',None),('DialogueText','text',None)])
q.write(f,'''(fn TurnInQuests (Player NPCID)
 (bind (count reply) (CallFunction|ProcessNPCInteraction :Player Player :TargetName NPCID :FallbackDialogue "You don't have any quests ready to turn in here."))
 (if (> count 0)
  (return count reply)
  (else
   (bind (pending pendingReply) (CallFunction|GetPendingQuestReply :Player Player :TargetName NPCID))
   (if pending (return 0 pendingReply)
    (else (return 0 "You don't have any quests ready to turn in here."))))))''')
# Pending collection feedback uses actual inventory instead of collected-event counters.
code=(q.AUDIT/'GetPendingQuestReply.dsl').read_text()
needle='(bind (progress exists) (Utilities|Map|Find (Class|BPPlayer|GetQuestProgress Player) (Utilities|String|ToString(Name) quest)))'
replacement='''(bind (kind itemType required) (CallFunction|GetObjectiveRequirement :QuestID quest))
      (bind (killProgress foundProgress) (Utilities|Map|Find (Class|BPPlayer|GetQuestProgress Player) (Utilities|String|ToString(Name) quest)))
      (bind (itemQuantity foundItems) (Utilities|Map|Find (Class|BPPlayer|GetInventoryItems Player) (Utilities|String|ToString(Name) itemType)))
      (bind progress (select (== kind (Utilities|String|StringToName "Collection")) itemQuantity killProgress))'''
assert needle in code;code=code.replace(needle,replacement)
q.write({'refPath':BANK+':GetPendingQuestReply'},code)
q.BANK=PICKUP
q.write({'refPath':PICKUP+':CollectForPlayer'},'''(fn CollectForPlayer (Player)
 (Utilities|IsValid Player
  (:"Is Valid"
   (if (not (Variables|Default|GetUsed))
    (bind bank (Class|BPPlayer|GetQuestBank Player))
    (Utilities|IsValid bank
     (:"Is Valid"
      (Variables|Default|SetUsed true)
      (bind added (Class|BPQuestBank|RecordCollectedItems :self bank :Player Player :ItemType (Variables|Default|GetObjectiveTargetType) :Amount 1))
      (if added (Actor|DestroyActor) (return true)
       (else (Variables|Default|SetUsed false) (return false))))
     (:"Is Not Valid" (return false)))
    (else (return false))))
  (:"Is Not Valid" (return false))))''')
# Choice-bearing NPCs greet the player; turn-in now happens through the menu.
q.BANK=NPC
code=(q.AUDIT/'ResolveQuestDialogue.dsl').read_text()
code=code.replace('(if (Variables|Default|GetCompletesQuestonInteract)', '(if (and (Variables|Default|GetCompletesQuestonInteract) (not (Variables|Default|GetHasChoices)))')
q.write({'refPath':NPC+':ResolveQuestDialogue'},code)
q.BANK=W
f=q.function('RequestBankTurnIn',[],[('Reply','text',None)])
q.write(f,'''(fn RequestBankTurnIn ()
 (bind player (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0))
  (:then
   (bind bank (Class|BPPlayer|GetQuestBank player))
   (Utilities|IsValid bank
    (:"Is Valid"
     (Utilities|IsValid (Variables|Default|GetNPCReference)
      (:"Is Valid"
       (bind npc (Class|BPNpc|ResolveQuestNPCID :self (Variables|Default|GetNPCReference)))
       (bind (count reply) (Class|BPQuestBank|TurnInQuests :self bank :Player player :NPCID npc))
       (return reply))
      (:"Is Not Valid" (return "This quest giver is unavailable."))))
    (:"Is Not Valid" (return "The quest bank is unavailable."))))
  (:CastFailed (return "The quest bank is unavailable."))))''')
f=q.function('HandleQuestTurnIn',[],[])
q.write(f,'''(fn HandleQuestTurnIn ()
 (bind reply (CallFunction|RequestBankTurnIn))
 (Widget|SetVisibility (Variables|WBP_Dialogue|GetVB_Choices) "Collapsed")
 (Widget|SetVisibility (Variables|WBP_Dialogue|GetTXT_Dialogue) "Visible")
 (Variables|Default|SetDialogueText reply)
 (Variables|Default|SetDialogueState 2)
 (return))''')
print('Turn-in backend saved',call('save_assets',{'asset_paths':[BANK,PLAYER,PICKUP,NPC,W]},'editor_toolset.toolsets.asset.AssetTools'))
