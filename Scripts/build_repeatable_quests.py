"""Apply the repeatable request extension through Unreal MCP. Editor-only."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import quest_bank_mcp as q
call=q.call; BANK=q.BANK; PLAYER=q.PLAYER
_catalog_path = q.ROOT / 'Docs/RepeatableQuestCatalog.json'
if _catalog_path.exists() and any(e.get('objectiveType') in ('Combat', 'Collection') for e in __import__('json').loads(_catalog_path.read_text())):
 raise SystemExit('This one-time migration is superseded by the installed mixed quest bank. Author quests through DT_Quests and their rule assets; see Docs/QuestBank.md.')

OBJ='editor_toolset.toolsets.object.ObjectTools'
ASSET='editor_toolset.toolsets.asset.AssetTools'
DT='editor_toolset.toolsets.data_table.DataTableTools'
DA='editor_toolset.toolsets.data_asset.DataAssetTools'

def addvar(bp,name,typ,container=None):
    if name not in call('list_variables',{'blueprint':{'refPath':bp}}):
        args={'blueprint':{'refPath':bp},'name':name,'type_name':typ}
        if container:args['container_type']=container
        call('add_variable',args)

def graph(name,code,locals=()):
    g={'refPath':BANK+':'+name}
    existing=call('list_variables',{'blueprint':{'refPath':BANK},'graph':g})
    for n,t in locals:
        if n not in existing:call('add_variable',{'blueprint':{'refPath':BANK},'graph':g,'name':n,'type_name':t})
    q.write(g,code)

addvar(BANK,'RepeatableQuestIDs','name','ARRAY')
addvar(BANK,'QuestWeights','int','MAP')
for name in ['RepeatableQuestIDs','QuestWeights']:
    call('set_variable_instance_editable',{'blueprint':{'refPath':BANK},'variable_name':name,'instance_editable':True})
addvar(PLAYER,'Gold','int')
call('compile_blueprint',{'blueprint':{'refPath':PLAYER},'warnings_as_errors':True})
call('compile_blueprint',{'blueprint':{'refPath':BANK},'warnings_as_errors':True})
baseline=q.AUDIT/'CheckQuestEligibility_before_repeatable.dsl'
if not baseline.exists():
    current=(q.AUDIT/'CheckQuestEligibility.dsl').read_text()
    current=current.replace('(and (Utilities|Array|ContainsItem (Class|BPPlayer|GetCompletedQuestIDs Player) QuestID) (not (Utilities|Array|ContainsItem (Variables|Default|GetRepeatableQuestIDs) QuestID)))','(Utilities|Array|ContainsItem (Class|BPPlayer|GetCompletedQuestIDs Player) QuestID)')
    baseline.write_text(current)
code=baseline.read_text()
code=code.replace('(Utilities|Array|ContainsItem (Class|BPPlayer|GetCompletedQuestIDs Player) QuestID)', '(and (Utilities|Array|ContainsItem (Class|BPPlayer|GetCompletedQuestIDs Player) QuestID) (not (Utilities|Array|ContainsItem (Variables|Default|GetRepeatableQuestIDs) QuestID)))')
graph('CheckQuestEligibility',code)
graph('RequestQuest','''(fn RequestQuest (Player GiverName)
 (bind available (CallFunction|GetAvailableQuestIDs :Player Player :GiverName GiverName))
 (Variables|Default|SetTotalWeight 0)
 (for quest available
   (if (not (Utilities|Array|ContainsItem (Variables|Default|GetRepeatableQuestIDs) quest))
     (bind (accepted reply) (CallFunction|TryAcceptQuest :Player Player :GiverName GiverName :QuestID quest))
     (return accepted quest reply))
   (bind (weight found) (Utilities|Map|Find (Variables|Default|GetQuestWeights) (Utilities|String|ToString(Name) quest)))
   (Variables|Default|SetTotalWeight (+ (Variables|Default|GetTotalWeight) (select (and found (> weight 0)) weight 1))))
 (if (> (Variables|Default|GetTotalWeight) 0)
   (Variables|Default|SetRoll (Math|Random|RandomIntegerinRange 1 (Variables|Default|GetTotalWeight)))
   (for quest available
     (bind (weight found) (Utilities|Map|Find (Variables|Default|GetQuestWeights) (Utilities|String|ToString(Name) quest)))
     (Variables|Default|SetRoll (- (Variables|Default|GetRoll) (select (and found (> weight 0)) weight 1)))
     (if (<= (Variables|Default|GetRoll) 0)
       (bind (accepted reply) (CallFunction|TryAcceptQuest :Player Player :GiverName GiverName :QuestID quest))
       (return accepted quest reply))))
 (return false (Utilities|String|StringToName "") "I don't have another available request for you right now."))''',[('TotalWeight','int'),('Roll','int')])
baseline=q.AUDIT/'TryCompleteQuest_before_repeatable.dsl'
if not baseline.exists():
    current=(q.AUDIT/'TryCompleteQuest.dsl').read_text()
    current=current.replace('\n           (Class|BPPlayer|SetGold :self Player :Gold (+ (Class|BPPlayer|GetGold Player) (select (> gold 0) gold 0)))','')
    current=current.replace('(Utilities|Array|RemoveItem (Class|BPPlayer|GetCompletedQuestIDs Player) QuestID)\n           ','')
    baseline.write_text(current)
code=baseline.read_text()
code=code.replace('(Utilities|Array|AddUnique (Class|BPPlayer|GetCompletedQuestIDs Player) QuestID)', '(Utilities|Array|RemoveItem (Class|BPPlayer|GetCompletedQuestIDs Player) QuestID)\n           (Utilities|Array|AddUnique (Class|BPPlayer|GetCompletedQuestIDs Player) QuestID)\n           (Class|BPPlayer|SetGold :self Player :Gold (+ (Class|BPPlayer|GetGold Player) (select (> gold 0) gold 0)))')
graph('TryCompleteQuest',code)
print('Core extension compiled.',flush=True)

# 40 distinct named commissions per tier; existing delivery remains untouched.
commodities=[
 ['Mint Cuttings','Chamomile Sachets','Clean Bandages','Candle Wicks','Copper Buttons','Blank Labels','Apple Seeds','Linen Thread','Lavender Sprigs','Wooden Stoppers'],
 ['Willow Bark','Sage Bundles','Glass Vials','Honey Jars','Healing Salve','Silver Needles','Cedar Resin','Blue Dye','Bitterroot Tea','Pressed Flowers'],
 ['Moonleaf Extract','Frostfern Samples','Ashwood Charcoal','Stormglass Flasks','Sunstone Dust','Nightbloom Seeds','Ironvine Fibres','Amber Tincture','Raven Ink','River Pearl Powder'],
 ['Phoenix Ash','Basilisk Antidote','Wyrmroot Oil','Thunder Lily Pollen','Obsidian Mortars','Ghost Orchid Essence','Starfall Fragments','Dragonseal Wax','Winterheart Sap','Eclipse Crystals'],
 ['Celestial Dew','Ancient Heartwood','Void Lotus Petals','Royal Cure Formula','Dawnfire Elixir','Astral Salt','Elder Dragon Tears','Worldroot Seed','Sovereign Seal','Everlight Nectar']]
contexts=[
 ('Clinic Restock','the town clinic needs a fresh supply before evening rounds'),
 ('Research Commission','Rein needs a carefully labelled batch for guild research'),
 ('Sealed Guild Order','the guild has commissioned a sealed consignment for Rein'),
 ('Emergency Reserve','Rein is replenishing the emergency reserve for the next expedition')]
rewards=[(15,1),(60,2),(180,5),(500,15),(1400,40)]
weights=[50,28,14,6,2];difficulties=['Easy','Normal','Hard','Insane','Elite']
rows={};rules={};ids=[];weightmap={};paths=[];catalog=[]
folder='/Game/Game/Quests/Repeatable'
call('create_folder',{'path':folder},ASSET)
for tier in range(1,6):
    for index in range(40):
        material=commodities[tier-1][index%10];context,reason=contexts[index//10]
        quest=f'RQ_{tier}Star_{index+1:03d}'
        amount=tier+index//10
        reward=rewards[tier-1][0]+rewards[tier-1][1]*index
        title=f'{tier}-Star: {material} - {context}'
        desc=f'{title}. {reason.capitalize()}. Deliver the {material.lower()} consignment to Rein. Guild rating: {tier}/5 stars. Reward: {reward} gold.'
        rows[quest]={'questId':quest,'questName':title,'description':desc,'objectiveText':f'Deliver {material.lower()} to Rein ({context.lower()}).','difficulty':difficulties[tier-1],'rewardGold':reward,'questGiver':'Luna','targetNPC':'Rein','requiredAmount':amount}
        name='DA_'+quest;path=folder+'/'+name+'.'+name
        if not call('exists',{'path':folder+'/'+name},ASSET):
            call('create',{'folder_path':folder,'asset_name':name,'asset_type':{'refPath':'/Game/Game/Quests/Blueprints/BP_QuestItemRule.BP_QuestItemRule_C'}},DA)
        # A stable type is shared by each material's four commission variants.
        itemtype=''.join(c for c in material if c.isalnum())
        values={'QuestID':quest,'SharedItemTypes':[itemtype],'CompletionText':f'The {material.lower()} consignment for {context.lower()} has arrived. Thank you! The guild awarded {reward} gold.','CompletedText':f'Thanks again for the {material.lower()} delivery. Luna has more guild commissions.'}
        call('set_properties',{'instance':{'refPath':path},'values':json.dumps(values)},OBJ)
        ids.append(quest);rules[quest]=path;weightmap[quest]=weights[tier-1];paths.append(path)
        catalog.append({'id':quest,'stars':tier,'title':title,'gold':reward,'itemType':itemtype})
    print('Created tier',tier,flush=True)
table={'refPath':q.TABLE}
existing=call('list_rows',{'data_table':table},DT)
missing=[i for i in ids if i not in existing]
if missing:call('add_rows',{'data_table':table,'row_names':missing},DT)
call('set_rows',{'data_table':table,'values':json.dumps(rows)},DT)
bank={'refPath':'/Game/Game/Quests/DA_QuestBank.DA_QuestBank'}
props=json.loads(call('get_properties',{'instance':bank,'properties':['ItemRules','RepeatableQuestIDs','QuestWeights']},OBJ))
# ObjectTools returns a property dictionary; retain unrelated existing configuration.
oldrules=props.get('ItemRules',{})
if not isinstance(oldrules,dict):raise RuntimeError(props)
oldrules.update(rules)
oldids=props.get('RepeatableQuestIDs',[]) or []
oldweights=props.get('QuestWeights',{}) or {};oldweights.update(weightmap)
call('set_properties',{'instance':bank,'values':json.dumps({'ItemRules':oldrules,'RepeatableQuestIDs':list(dict.fromkeys(oldids+ids)),'QuestWeights':oldweights})},OBJ)
for bp in [BANK,PLAYER,'/Game/Game/Characters/NPCs/BP_Npc.BP_Npc','/Game/Game/Characters/NPCs/WBP_Dialogue.WBP_Dialogue']:
    call('compile_blueprint',{'blueprint':{'refPath':bp},'warnings_as_errors':True})
paths += [BANK,PLAYER,q.TABLE,bank['refPath']]
print('Saved',call('save_assets',{'asset_paths':paths},ASSET),flush=True)
Path('Docs/RepeatableQuestCatalog.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
(q.AUDIT/'repeatable_assets.json').write_text(json.dumps(paths,indent=2))
