"""Focused editor migration for consistent dialogue-choice typography and layout."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import quest_bank_mcp as q
W='/Game/Game/Characters/NPCs/WBP_Dialogue.WBP_Dialogue';q.BANK=W
OBJ='editor_toolset.toolsets.object.ObjectTools'
reference=json.loads(q.call('get_properties',{'instance':{'refPath':W+':WidgetTree.TextChoice1'},'properties':['Font','ColorAndOpacity']},OBJ))
for index in range(1,5):
 text={'refPath':W+':WidgetTree.TextChoice'+str(index)}
 q.call('set_properties',{'instance':text,'values':json.dumps(dict(reference,Justification='Left'))},OBJ)
 for name,alignment in [('TextChoice','HAlign_Left'),('Choice','HAlign_Fill')]:
  widget={'refPath':W+':WidgetTree.'+name+str(index)}
  slot=json.loads(q.call('get_properties',{'instance':widget,'properties':['Slot']},OBJ))['Slot']
  values={'HorizontalAlignment':alignment,'VerticalAlignment':'VAlign_Center' if name=='TextChoice' else 'VAlign_Fill','Padding':{'left':4,'top':2,'right':4,'bottom':2} if name=='TextChoice' else {'left':0,'top':0,'right':0,'bottom':0}}
  if name == 'Choice': values['Size'] = {'value': 1, 'sizeRule': 'Automatic'}
  q.call('set_properties',{'instance':slot,'values':json.dumps(values)},OBJ)
code=(q.AUDIT/'EnsureTurnInChoice.dsl').read_text()
if '(bind button ' not in code:
 code=code.replace('   (Variables|Default|SetTurnInExitWidget', '''   (bind button (Game|ConstructObjectfromClass :Class "/Script/UMG.Button" :self (Variables|Getareferencetoself)))
   (Button|Appearance|SetStyle :self button :InStyle (Class|Button|GetStyle :self (Variables|WBP_Dialogue|GetChoice1)))
   (bind textSlot (Widget|Panel|AddChild :self button :Content choice))
   (bind buttonSlot (Utilities|Casting|CastToButtonSlot :Object textSlot))
   (Layout|ButtonSlot|SetHorizontalAlignment :self buttonSlot :InHorizontalAlignment "HAlign_Left")
   (Layout|ButtonSlot|SetPadding :self buttonSlot :InPadding (Utilities|Struct|MakeMargin :Left 4.0 :Top 2.0 :Right 4.0 :Bottom 2.0))
   (Variables|Default|SetTurnInExitWidget''',1)
 code=code.replace(':Content choice))\n   (bind restored', ':Content button))\n   (bind restored')
 code=code.replace('   (return))))','''   (Layout|VerticalBoxSlot|SetHorizontalAlignment :self added :InHorizontalAlignment "HAlign_Fill")
   (Layout|VerticalBoxSlot|SetHorizontalAlignment :self restored :InHorizontalAlignment "HAlign_Fill")
   (return))))''')
code=code.replace('(Variables|WBP_Dialogue|GetChoice1)', '(Utilities|Casting|CastToButton :Object (Widget|GetParent :self (Variables|WBP_Dialogue|GetTextChoice1)))')
q.write({'refPath':W+':EnsureTurnInChoice'},code)
# The property action only assigns Font. Use UTextBlock.SetFont so Slate updates too.
graph={'refPath':W+':EnsureTurnInChoice'}
nodes=q.call('get_node_infos',{'nodes':q.call('find_nodes',{'graph':graph,'title':''})})
old=next(n for n in nodes if any(p['name']=='Font' for p in n['input_pins']) and any(p['name']=='Output_Get' for p in n['output_pins']))
new=q.call('create_node',{'graph':graph,'type_id':'Appearance|SetFont','declaring_class':{'refPath':'/Script/UMG.TextBlock'},'pos':old['position']})
newinfo=q.call('get_node_infos',{'nodes':[new]})[0]
for direction in ['input_pins','output_pins']:
 for pin in old[direction]:
  name={'Font':'InFontInfo'}.get(pin['name'],pin['name'])
  target=next((p for p in newinfo[direction] if p['name']==name),None)
  for connected in pin['connected_pins']:
   if not target:raise RuntimeError('Cannot safely transfer '+name)
   output,inputpin=(connected,pin['pin_id']) if direction=='input_pins' else (pin['pin_id'],connected)
   q.call('break_pins',{'output_pin':output,'input_pin':inputpin})
   output,inputpin=(connected,target['pin_id']) if direction=='input_pins' else (target['pin_id'],connected)
   q.call('connect_pins',{'output_pin':output,'input_pin':inputpin})
q.call('compile_blueprint',{'blueprint':{'refPath':W},'warnings_as_errors':True})
print('Saved',q.call('save_assets',{'asset_paths':[W]},'editor_toolset.toolsets.asset.AssetTools'))
