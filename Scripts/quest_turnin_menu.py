import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import quest_bank_mcp as q
W='/Game/Game/Characters/NPCs/WBP_Dialogue.WBP_Dialogue'
q.BANK=W
if 'TurnInChoiceText' not in q.call('list_variables',{'blueprint':{'refPath':W}}):
 q.call('add_object_variable',{'blueprint':{'refPath':W},'name':'TurnInChoiceText','object_class':{'refPath':'/Script/UMG.TextBlock'}})
if 'TurnInExitWidget' not in q.call('list_variables',{'blueprint':{'refPath':W}}):
 q.call('add_object_variable',{'blueprint':{'refPath':W},'name':'TurnInExitWidget','object_class':{'refPath':'/Script/UMG.Widget'}})
f=q.function('EnsureTurnInChoice',[],[])
q.write(f,'''(fn EnsureTurnInChoice ()
 (Utilities|IsValid (Variables|Default|GetTurnInChoiceText)
  (:"Is Valid" (return))
  (:"Is Not Valid"
   (bind choice (Game|ConstructObjectfromClass :Class "/Script/UMG.TextBlock" :self (Variables|Getareferencetoself)))
   (Variables|Default|SetTurnInChoiceText choice)
   (Class|Text|SetFont :self choice :Font (Class|Text|GetFont :self (Variables|WBP_Dialogue|GetTextChoice1)))
   (Class|Text|SetColorandOpacity :self choice :ColorAndOpacity (Class|Text|GetColorandOpacity :self (Variables|WBP_Dialogue|GetTextChoice1)))
   (Widget|SetText(Text) :self choice :InText "Turn in Quest Items")
   (Variables|Default|SetTurnInExitWidget (Widget|Panel|GetChildAt :self (Variables|WBP_Dialogue|GetVB_Choices) :Index 3))
   (bind removed (Widget|Panel|RemoveChild :self (Variables|WBP_Dialogue|GetVB_Choices) :Content (Variables|Default|GetTurnInExitWidget)))
   (bind added (Panel|AddChildtoVerticalBox :self (Variables|WBP_Dialogue|GetVB_Choices) :Content choice))
   (bind restored (Panel|AddChildtoVerticalBox :self (Variables|WBP_Dialogue|GetVB_Choices) :Content (Variables|Default|GetTurnInExitWidget)))
   (return))))''')
labels=[('TextChoice1',0,"I'd like to take on a request."),('TextChoice2',1,"Tell me about the Adventurer's Guild."),('TextChoice3',2,'Is there anything I should know about the area?'),('TurnInChoiceText',3,'Turn in Quest Items'),('TextChoice4',4,'Nothing right now.')]
lines=['(fn UpdateChoiceVisual ()',' (CallFunction|EnsureTurnInChoice)']
for var,index,label in labels:
 getter=('Variables|Default|Get' if var=='TurnInChoiceText' else 'Variables|WBP_Dialogue|Get')+var
 lines.append(f' (Widget|SetText(Text) :self ({getter}) :InText (select (== (Variables|Default|GetSelectedChoice) {index}) {json.dumps("> "+label)} {json.dumps(label)}))')
lines+=[' (return))']
q.write({'refPath':W+':UpdateChoiceVisual'},'\n'.join(lines))
# Preserve existing guild/advice/exit responses and E repeat handling.
code=(q.AUDIT/'Dialogue_OnKeyDown.dsl').read_text()
start=code.index('            (:0',code.index('(:1'))
end=code.index('            (:1',start)
code=code[:start]+'            (:0 (CallFunction|HandleQuestRequest))\n'+code[end:]
code=code.replace('            (:3\n','            (:3 (CallFunction|HandleQuestTurnIn))\n            (:4\n',1)
start=code.index('    (elif (Input|Key|Equal(Key) "W"')
code=code[:start]+'''    (elif (Input|Key|Equal(Key) "W" (Input|KeyEvent|GetKey InKeyEvent))
     (if (== (Variables|Default|GetDialogueState) 1)
      (Variables|Default|SetSelectedChoice (select (== (Variables|Default|GetSelectedChoice) 0) 4 (- (Variables|Default|GetSelectedChoice) 1)))
      (CallFunction|UpdateChoiceVisual))
     (elif (Input|Key|Equal(Key) "S" (Input|KeyEvent|GetKey InKeyEvent))
      (if (== (Variables|Default|GetDialogueState) 1)
       (Variables|Default|SetSelectedChoice (select (>= (Variables|Default|GetSelectedChoice) 4) 0 (+ (Variables|Default|GetSelectedChoice) 1)))
       (CallFunction|UpdateChoiceVisual)))))
 (return (Widget|EventReply|Handled)))'''
code=code.replace('Input|Key|Equal(Key)', 'Utilities|String|EqualExactly(String)').replace('(Input|KeyEvent|GetKey InKeyEvent)', '(Utilities|String|ToString(Text) (Input|Key|GetKeyDisplayName (Input|KeyEvent|GetKey InKeyEvent)))').replace('Widget|GetInputEventFromKeyEvent','Widget|GetInputEventfromKeyEvent')
q.write({'refPath':W+':OnKeyDown'},code)
print(q.call('save_assets',{'asset_paths':[W]},'editor_toolset.toolsets.asset.AssetTools'))


