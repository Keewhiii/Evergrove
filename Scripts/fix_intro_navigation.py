"""Enable native mouse hit-box events and clarify options navigation."""
from build_companion_combat import *
M='/Game/Game/UI/BP_EvergroveIntroHUD.BP_EvergroveIntroHUD'
code=(ROOT/'Saved/CombatAudit/InitializeMenu.dsl').read_text()
if 'SetEnableClickEvents' not in code:
 code=code.replace(' (Variables|Default|SetStatus', ''' (Class|PlayerController|SetEnableClickEvents :self (Game|GetPlayerController 0) :bEnableClickEvents true)
 (Class|PlayerController|SetEnableMouseOverEvents :self (Game|GetPlayerController 0) :bEnableMouseOverEvents true)
 (Variables|Default|SetStatus''')
code=code.replace('(Input|SetInputModeGameOnly :PlayerController (Game|GetPlayerController 0) :bFlushInput true)','(Input|SetInputModeGameAndUI :PlayerController (Game|GetPlayerController 0) :InMouseLockMode "DoNotLock" :bHideCursorDuringCapture false :bFlushInput true)')
graph(M,'InitializeMenu',code)
travel=(ROOT/'Saved/CombatAudit/UpdateMenu.dsl').read_text()
if 'SetInputModeGameOnly' not in travel:travel=travel.replace('   (Class|PlayerController|SetShowMouseCursor','   (Input|SetInputModeGameOnly :PlayerController (Game|GetPlayerController 0) :bFlushInput true)\n   (Class|PlayerController|SetShowMouseCursor')
graph(M,'UpdateMenu',travel,[('Delta','float',None)])
code=(ROOT/'Saved/CombatAudit/DrawOptions.dsl').read_text()
hint='''(HUD|DrawText :Text "Click a setting or its arrows  |  Arrow keys: select / adjust  |  Esc: back" :TextColor (Math|Color|MakeColor 0.94 0.87 0.68 1.0) :ScreenX (+ (Variables|Default|GetUIX) (* 128.0 (Variables|Default|GetUIScale))) :ScreenY (+ (Variables|Default|GetUIY) (* 687.0 (Variables|Default|GetUIScale))) :Font "/Game/Game/UI/Evergrove/F_EvergroveStory.F_EvergroveStory" :Scale (* 0.3541666667 (Variables|Default|GetUIScale)))'''
if 'Arrow keys:' not in code:
 code=code.rstrip()[:-1]+'\n'+hint+')'
 graph(M,'DrawOptions',code)
call('compile_blueprint',{'blueprint':ref(M),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[M]},ASSET)
print('MOUSE_OPTIONS_NAVIGATION_SAVED',flush=True)
