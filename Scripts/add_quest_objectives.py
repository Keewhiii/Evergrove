"""Extend existing Quest Bank using Unreal MCP only."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import quest_bank_mcp as q
call=q.call;BANK=q.BANK;PLAYER=q.PLAYER;RULE='/Game/Game/Quests/Blueprints/BP_QuestItemRule.BP_QuestItemRule'
_catalog_path = q.ROOT / 'Docs/RepeatableQuestCatalog.json'
if _catalog_path.exists() and any(e.get('objectiveType') in ('Combat', 'Collection') for e in __import__('json').loads(_catalog_path.read_text())):
 raise SystemExit('This one-time migration is superseded by the installed mixed quest bank. Author quests through DT_Quests and their rule assets; see Docs/QuestBank.md.')

OBJ='editor_toolset.toolsets.object.ObjectTools';ASSET='editor_toolset.toolsets.asset.AssetTools'
P=PLAYER+'_C'
def add(bp,name,t,c=None,editable=False):
 if name not in call('list_variables',{'blueprint':{'refPath':bp}}):
  args={'blueprint':{'refPath':bp},'name':name,'type_name':t}
  if c:args['container_type']=c
  call('add_variable',args)
 if editable:call('set_variable_instance_editable',{'blueprint':{'refPath':bp},'variable_name':name,'instance_editable':True})
add(PLAYER,'QuestProgress','int','MAP')
add(RULE,'ObjectiveType','name',editable=True)
add(RULE,'ObjectiveTargetType','name',editable=True)
for bp in [PLAYER,RULE]:call('compile_blueprint',{'blueprint':{'refPath':bp},'warnings_as_errors':True})

f=q.function('GetObjectiveRequirement',[('QuestID','name',None)],[('Kind','name',None),('TargetType','name',None),('Required','int',None)])
q.write(f,'''(fn GetObjectiveRequirement (QuestID)
 (bind (rule exists) (Utilities|Map|Find (Variables|QuestBank|GetItemRules) (Utilities|String|ToString(Name) QuestID)))
 (if exists
  (Utilities|IsValid rule
   (:"Is Valid"
    (if (== (Class|BPQuestItemRule|GetQuestID rule) QuestID)
     (bind (found data) (CallFunction|GetQuestData :QuestID QuestID))
     (if found
      (bind (id title description objective difficulty gold giver target amount) (Utilities|Struct|BreakSTQuestData data))
      (return (Class|BPQuestItemRule|GetObjectiveType rule) (Class|BPQuestItemRule|GetObjectiveTargetType rule) (select (> amount 0) amount 1))
      (else (return "Delivery" "None" 1)))
     (else (return "Delivery" "None" 1))))
   (:"Is Not Valid" (return "Delivery" "None" 1)))
  (else (return "Delivery" "None" 1))))''')
f=q.function('IsQuestObjectiveReady',[('Player',P,None),('QuestID','name',None)],[('Ready','bool',None)])
q.write(f,'''(fn IsQuestObjectiveReady (Player QuestID)
 (Utilities|IsValid Player
  (:"Is Valid"
   (bind (kind target required) (CallFunction|GetObjectiveRequirement :QuestID QuestID))
   (if (or (== kind (Utilities|String|StringToName "Combat")) (== kind (Utilities|String|StringToName "Collection")))
    (bind (progress found) (Utilities|Map|Find (Class|BPPlayer|GetQuestProgress Player) (Utilities|String|ToString(Name) QuestID)))
    (return (and found (>= progress required)))
    (else (return true))))
  (:"Is Not Valid" (return false))))''')
f=q.function('ReportObjectiveProgress',[('Player',P,None),('Kind','name',None),('TargetType','name',None),('Amount','int',None)],[('UpdatedQuests','int',None)],[('Updated','int',None)])
q.write(f,'''(fn ReportObjectiveProgress (Player Kind TargetType Amount)
 (Variables|Default|SetUpdated 0)
 (Utilities|IsValid Player
  (:"Is Valid"
   (if (and (> Amount 0) (or (== Kind (Utilities|String|StringToName "Combat")) (== Kind (Utilities|String|StringToName "Collection"))))
    (for quest (Class|BPPlayer|GetActiveQuestIDs Player)
     (bind (objective target required) (CallFunction|GetObjectiveRequirement :QuestID quest))
     (if (and (== objective Kind) (== target TargetType))
      (bind (current found) (Utilities|Map|Find (Class|BPPlayer|GetQuestProgress Player) (Utilities|String|ToString(Name) quest)))
      (if (< current required)
       (Utilities|Map|Add (Class|BPPlayer|GetQuestProgress Player) (Utilities|String|ToString(Name) quest) (select (> (+ current Amount) required) required (+ current Amount)))
       (Variables|Default|SetUpdated (+ (Variables|Default|GetUpdated) 1))))))
   (return (Variables|Default|GetUpdated)))
  (:"Is Not Valid" (return 0))))''')
# Replays start at zero progress; legacy delivery keeps its original behavior.
code=(q.AUDIT/'TryAcceptQuest.dsl').read_text()
needle='(Utilities|Array|AddUnique (Class|BPPlayer|GetActiveQuestIDs Player) QuestID)'
if 'GetQuestProgress' not in code:code=code.replace(needle,needle+'\n     (Utilities|Map|Add (Class|BPPlayer|GetQuestProgress Player) (Utilities|String|ToString(Name) QuestID) 0)')
q.write({'refPath':BANK+':TryAcceptQuest'},code)
code=(q.AUDIT/'TryCompleteQuest.dsl').read_text()
code=code.replace('(and (== id QuestID) (== target TargetName))','(and (and (== id QuestID) (== target TargetName)) (CallFunction|IsQuestObjectiveReady :Player Player :QuestID QuestID))')
needle='(Utilities|Array|RemoveItem (Class|BPPlayer|GetActiveQuestIDs Player) QuestID)'
if 'Map|Remove' not in code:code=code.replace(needle,needle+'\n           (Utilities|Map|Remove (Class|BPPlayer|GetQuestProgress Player) (Utilities|String|ToString(Name) QuestID))')
q.write({'refPath':BANK+':TryCompleteQuest'},code)
call('save_assets',{'asset_paths':[PLAYER,RULE,BANK]},ASSET)
print('Objective tracking and turn-in gate saved.',flush=True)
