from build_companion_combat import *
P='/Game/Game/World/BP_MapPassage.BP_MapPassage'
for n,t in [('CaptureRequested','bool'),('CaptureCommand','string')]:
 var(P,n,t);call('set_variable_instance_editable',{'blueprint':ref(P),'variable_name':n,'instance_editable':True})
code='''(event EventTick (DeltaSeconds)
 (if (Variables|Default|GetCaptureRequested) (Variables|Default|SetCaptureRequested false) (Development|ExecuteConsoleCommand :Command (Variables|Default|GetCaptureCommand) :SpecificPlayer (Game|GetPlayerController 0)))
 (Variables|Default|SetAge (+ (Variables|Default|GetAge) DeltaSeconds))
 (if (and (> (Variables|Default|GetAge) 1.0) (not (Variables|Default|GetTravelDone)))
  (if (or (Variables|Default|GetRequested) (< (Math|Vector|Distance(Vector) (Transformation|GetActorLocation :self (Game|GetPlayerCharacter 0)) (Transformation|GetActorLocation)) (Variables|Default|GetRadius))) (CallFunction|Travel))))'''
graph(P,'EventGraph',code);call('compile_blueprint',{'blueprint':ref(P),'warnings_as_errors':True});call('save_assets',{'asset_paths':[P]},ASSET)
