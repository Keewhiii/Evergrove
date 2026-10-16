from build_companion_combat import *
T='/Game/Tests/World/BP_ForestTravelValidation.BP_ForestTravelValidation'
create(T,'/Script/Engine.Actor')
for n,t in [('Moving','bool'),('Direction','Vector'),('Requested','bool'),('GoldValue','int')]:
 var(T,n,t);call('set_variable_instance_editable',{'blueprint':ref(T),'variable_name':n,'instance_editable':True})
graph(T,'EventGraph','''(event EventTick (DeltaSeconds)
 (if (Variables|Default|GetMoving) (Pawn|Input|AddMovementInput :self (Game|GetPlayerCharacter 0) :WorldDirection (Variables|Default|GetDirection) :ScaleValue 1.0))
 (if (Variables|Default|GetRequested)
  (Variables|Default|SetRequested false)
  (bind hero (Utilities|Casting|CastToBP_Player :Object (Game|GetPlayerCharacter 0)) (:then (Class|BPPlayer|SetGold :self hero :Gold (Variables|Default|GetGoldValue))) (:CastFailed))))''')
call('save_assets',{'asset_paths':[T]},ASSET)
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
for fn in ['EnsureCozy','CreateLanternLights']:
 code=(ROOT/'Saved/CombatAudit'/(fn+'.dsl')).read_text()
 code=code.replace('(fn '+fn+' ()','(fn '+fn+' ()\n (if (Utilities|String|EqualExactly(String) (Game|GetCurrentLevelName :bRemovePrefixString true) "L_EvergroveForest") (return))',1)
 graph(W,fn,code)
call('compile_blueprint',{'blueprint':ref(W),'warnings_as_errors':True});call('save_assets',{'asset_paths':[W]},ASSET)
