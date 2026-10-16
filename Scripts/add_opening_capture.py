from build_companion_combat import *
O='/Game/Game/UI/BP_EvergroveOpeningHUD.BP_EvergroveOpeningHUD'
for n,t in [('CaptureRequested','bool'),('CaptureCommand','string')]:
 var(O,n,t);call('set_variable_instance_editable',{'blueprint':ref(O),'variable_name':n,'instance_editable':True})
code=(ROOT/'Saved/CombatAudit/UpdateSequence.dsl').read_text()
if 'CaptureRequested' not in code:code=code.replace('(fn UpdateSequence (Delta)','''(fn UpdateSequence (Delta)
 (if (Variables|Default|GetCaptureRequested) (Variables|Default|SetCaptureRequested false) (Development|ExecuteConsoleCommand :Command (Variables|Default|GetCaptureCommand) :SpecificPlayer (Game|GetPlayerController 0)))''',1)
graph(O,'UpdateSequence',code,[('Delta','float',None)])
call('compile_blueprint',{'blueprint':ref(O),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[O]},ASSET)
