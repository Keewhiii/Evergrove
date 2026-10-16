from build_companion_combat import *
T='/Game/Tests/World/BP_IntroValidation.BP_IntroValidation'
M='/Game/Game/UI/BP_EvergroveIntroHUD.BP_EvergroveIntroHUD'
create(T,'/Script/Engine.Actor')
graph(T,'ValidObject','''(fn ValidObject (Object) (Utilities|IsValid Object (:"Is Valid" (return true)) (:"Is Not Valid" (return false))))''',[('Object','/Script/CoreUObject.Object',None)],[('Valid','bool',None)])
for n,t in [('Requested','bool'),('Action','int'),('ScreenshotCommand','string'),('Menu',M+'_C')]:
 var(T,n,t)
 if n!='Menu':call('set_variable_instance_editable',{'blueprint':ref(T),'variable_name':n,'instance_editable':True})
graph(T,'CacheMenu','''(fn CacheMenu () (bind menu (Utilities|Casting|CastToBP_EvergroveIntroHUD :Object (HUD|GetHUD :self (Game|GetPlayerController 0))) (:then (Variables|Default|SetMenu menu)) (:CastFailed)))''')
menu='(Variables|Default|GetMenu)'
code='(event EventTick (DeltaSeconds) (if (Variables|Default|GetRequested) (Variables|Default|SetRequested false) (CallFunction|CacheMenu) (if (CallFunction|ValidObject :Object (Variables|Default|GetMenu))\n'
for i,fn in enumerate(['RefreshSave','Activate','Back','ApplyOptions','ReadOptions','ResetOptions']):code+=f'(if (== (Variables|Default|GetAction) {i}) (Class|BPEvergroveIntroHUD|{fn} :self {menu}))\n'
for i,fn in [(7,'LoadPreferences'),(8,'ApplyPreferences')]:code+=f'(if (== (Variables|Default|GetAction) {i}) (Class|BPEvergroveGameInstance|{fn} :self (Class|BPEvergroveIntroHUD|GetInstance :self {menu})))\n'
code+=f'(if (== (Variables|Default|GetAction) 9) (Class|BPEvergroveIntroHUD|HandleHit :self {menu} :BoxName (Utilities|Name|MakeLiteralName "Page0_Item2")))\n'
code+=f'(if (== (Variables|Default|GetAction) 10) (Class|BPEvergroveIntroHUD|MenuDown :self {menu}))\n'
for i,fn in [(11,'MenuRight'),(12,'MenuLeft')]:code+=f'(if (== (Variables|Default|GetAction) {i}) (Class|BPEvergroveIntroHUD|{fn} :self {menu}))\n'
code+=f'(if (== (Variables|Default|GetAction) 13) (Class|BPEvergroveIntroHUD|HandleHit :self {menu} :BoxName (Utilities|Name|MakeLiteralName "Option5_Plus")))\n'
code+=f'(if (== (Variables|Default|GetAction) 14) (Class|BPEvergroveIntroHUD|HandleHover :self {menu} :BoxName (Utilities|Name|MakeLiteralName "Option5_Minus")))\n'
code+='(if (== (Variables|Default|GetAction) 6) (Development|ExecuteConsoleCommand :Command (Variables|Default|GetScreenshotCommand) :SpecificPlayer (Game|GetPlayerController 0)))\n)))'
graph(T,'EventGraph',code)
defaults(T,{'Requested':False,'Action':0})
call('save_assets',{'asset_paths':[T]},ASSET)
print('INTRO_PROBE_READY',flush=True)
