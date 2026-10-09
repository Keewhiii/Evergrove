import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import quest_bank_mcp as q
from quest_description_text import format_quest_description
call=q.call;OBJ='editor_toolset.toolsets.object.ObjectTools';ASSET='editor_toolset.toolsets.asset.AssetTools'
catalog=json.loads(Path('Docs/RepeatableQuestCatalog.json').read_text());rows={};paths=[]
enemies=['Forest Slime','Wild Boar','Cave Bat','Thorn Wolf','Road Bandit','Moss Beetle','Stone Wisp','Marsh Spider','Ash Imp','Rogue Golem']
locations=['Meadow Path','Pine Hollow','Old Ruins','Riverbank','North Road']
for entry in catalog:
 tier=entry['stars'];index=int(entry['id'].split('_')[-1])-1;gold=entry['gold']
 original=entry.get('deliveryTitle',entry['title']);entry['deliveryTitle']=original
 material,context=original.split(': ',1)[1].split(' - ')
 path='/Game/Game/Quests/Repeatable/DA_'+entry['id']+'.DA_'+entry['id']
 kind='Delivery' if index<14 else ('Combat' if index<27 else 'Collection')
 itemtype=''.join(c for c in material if c.isalnum())
 if kind=='Combat':
  enemy=enemies[(index-14)%10];where=locations[(index-14)//3];target='Tier'+str(tier)+''.join(c for c in enemy if c.isalnum())
  amount=2*tier+(index-14)%3
  title=f'{tier}-Star: {enemy} Hunt - {where}'
  objective=f'Defeat {amount} {enemy.lower()} targets, then report to Luna.'
  desc=''  # Formatted after the catalog metadata below.
  completion=f'The {enemy.lower()} hunt is complete. The guild awarded {gold} gold.'
  shared=[]
 elif kind=='Collection':
  target=itemtype;amount=3*tier+(index-27)%4
  title=f'{tier}-Star: Gather {material} - {context}'
  objective=f'Collect {amount} {material.lower()} samples, then report to Luna.'
  desc=''  # Formatted after the catalog metadata below.
  completion=f'All {amount} {material.lower()} samples are accounted for. The guild awarded {gold} gold.'
  shared=[itemtype]
 else:
  target=itemtype;amount=tier+index//10;title=original
  objective=f'Deliver {material.lower()} to Rein ({context.lower()}).'
  reasons=['the town clinic needs a fresh supply before evening rounds','Rein needs a carefully labelled batch for guild research']
  desc=''  # Formatted after the catalog metadata below.
  completion=f'The {material.lower()} consignment for {context.lower()} has arrived. Thank you! The guild awarded {gold} gold.'
  shared=[itemtype]
 rows[entry['id']]={'questName':title,'description':desc,'objectiveText':objective,'requiredAmount':amount,'targetNPC':'Rein' if kind=='Delivery' else 'Luna'}
 call('set_properties',{'instance':{'refPath':path},'values':json.dumps({'ObjectiveType':kind,'ObjectiveTargetType':target,'SharedItemTypes':shared,'CompletionText':completion,'CompletedText':'Thanks again for completing '+title+'. Luna has more guild requests.'})},OBJ)
 entry.update({'title':title,'objectiveType':kind,'targetType':target,'requiredAmount':amount,'itemType':itemtype if shared else None,'turnInNPC':'Rein' if kind=='Delivery' else 'Luna'})
 rows[entry['id']]['description']=format_quest_description(entry)
 paths.append(path)
 if index==39:print('Mixed tier',tier,flush=True)
call('set_rows',{'data_table':{'refPath':q.TABLE},'values':json.dumps(rows)},'editor_toolset.toolsets.data_table.DataTableTools')
Path('Docs/RepeatableQuestCatalog.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
paths.append(q.TABLE)
print('Saved mixed catalog',call('save_assets',{'asset_paths':paths},ASSET))
