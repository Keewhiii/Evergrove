import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import quest_bank_mcp as q
T='/Game/Tests/QuestBank/BP_QuestBankValidation.BP_QuestBankValidation';q.BANK=T
if 'SavedInventory' not in q.call('list_variables',{'blueprint':{'refPath':T}}):
 q.call('add_variable',{'blueprint':{'refPath':T},'name':'SavedInventory','type_name':'int','container_type':'MAP'})
for name in ['RunRepeatableSuite','RunWeightedBatch']:
 code=(q.AUDIT/(name+'.dsl')).read_text()
 if name=='RunRepeatableSuite':
  code=code.replace('Class|BPQuestBank|ReportObjectiveProgress :self bank :Player player :Kind eliteKind :TargetType eliteTarget', 'Class|BPQuestBank|RecordCollectedItems :self bank :Player player :ItemType eliteTarget')
 else:
  needle='   (bind advanced (Class|BPQuestBank|ReportObjectiveProgress :self bank :Player player :Kind kind :TargetType target :Amount required))'
  code=code.replace(needle,'''   (if (== kind (Utilities|String|StringToName "Collection"))
    (bind collected (Class|BPQuestBank|RecordCollectedItems :self bank :Player player :ItemType target :Amount required))
    (else (bind advanced (Class|BPQuestBank|ReportObjectiveProgress :self bank :Player player :Kind kind :TargetType target :Amount required))))''')
 q.write({'refPath':T+':'+name},code)
code=(q.AUDIT/'RunObjectiveSuite.dsl').read_text()
code=code.replace(' (bind bank ', ' (Utilities|Map|Clear (Class|BPPlayer|GetInventoryItems player))\n (bind bank ',1)
code=code.replace(' (bind combatComplete ',''' (CallFunction|ValidateCondition :Condition (== (Class|BPPlayer|GetGold player) 0) :Message "Greeting Luna does not automatically turn in combat")
 (bind widget (UserInterface|CreateWidget :Class "/Game/Game/Characters/NPCs/WBP_Dialogue.WBP_Dialogue_C" :OwningPlayer (Game|GetPlayerController 0)))
 (Class|WBPDialogue|SetNPCReference :self widget :NPCReference (Variables|Default|GetLunaNPC))
 (Class|WBPDialogue|UpdateChoiceVisual :self widget)
 (Class|WBPDialogue|UpdateChoiceVisual :self widget)
 (bind choices (Widget|Panel|GetChildrenCount :self (Class|WBPDialogue|GetVB_Choices widget)))
 (CallFunction|ValidateCondition :Condition (== choices 5) :Message "Menu contains five choices without duplicate turn-in rows")
 (bind turnInReply (Class|WBPDialogue|RequestBankTurnIn :self widget))
 (bind combatComplete ''',1)
code=code.replace(' (bind collectionComplete ',''' (CallFunction|ValidateCondition :Condition (== (Class|BPPlayer|GetGold player) 29) :Message "Greeting Luna does not automatically consume gathered items")
 (bind gatherReply (Class|WBPDialogue|RequestBankTurnIn :self widget))
 (bind (remaining remainingFound) (Utilities|Map|Find (Class|BPPlayer|GetInventoryItems player) "LinenThread"))
 (CallFunction|ValidateCondition :Condition (== remaining 0) :Message "Gathering turn-in consumes required item quantity")
 (bind duplicateReply (Class|WBPDialogue|RequestBankTurnIn :self widget))
 (bind collectionComplete ''',1)
code=code.replace(' (bind (repeatComplete repeatReply)', ''' (bind fakeReady (Class|BPQuestBank|IsQuestObjectiveReady :self bank :Player player :QuestID "RQ_1Star_028"))
 (CallFunction|ValidateCondition :Condition (not fakeReady) :Message "Collection event counters alone cannot replace inventory")
 (bind added (Class|BPQuestBank|RecordCollectedItems :self bank :Player player :ItemType "LinenThread" :Amount 5))
 (bind (repeatComplete repeatReply)''',1)
code=code.replace(' (return))',''' (bind (excess excessFound) (Utilities|Map|Find (Class|BPPlayer|GetInventoryItems player) "LinenThread"))
 (CallFunction|ValidateCondition :Condition (== excess 2) :Message "Turn-in preserves surplus inventory items")
 (return))''')
q.write({'refPath':T+':RunObjectiveSuite'},code)
code=(q.AUDIT/'EventGraph.dsl').read_text()
code=code.replace('   (Variables|Default|SetSavedGold', '   (Variables|Default|SetSavedInventory (Class|BPPlayer|GetInventoryItems player))\n   (Variables|Default|SetSavedGold',1)
code=code.replace('   (Class|BPPlayer|SetGold', '   (Class|BPPlayer|SetInventoryItems :self player :InventoryItems (Variables|Default|GetSavedInventory))\n   (Class|BPPlayer|SetGold',1)
q.write({'refPath':T+':EventGraph'},code)
q.call('remove_function_graph',{'blueprint':{'refPath':T},'graph_name':'ProbeTextBlockConstruction'})
print(q.call('save_assets',{'asset_paths':[T]},'editor_toolset.toolsets.asset.AssetTools'))
