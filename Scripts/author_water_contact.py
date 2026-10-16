from build_companion_combat import *
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld';C='/Game/Environment/ForestFeatures/MPC_WaterInteraction.MPC_WaterInteraction'
code=(ROOT/'Saved/ForestRecoveryBackup/WaterBeforeAdjustment/WorldEventGraph.dsl').read_text()
code=code.replace('(CallFunction|AdvanceWorldClock DeltaSeconds)','(CallFunction|AdvanceWorldClock :Delta DeltaSeconds)').replace('(CallFunction|UpdateCamera DeltaSeconds)','(CallFunction|UpdateCamera :Delta DeltaSeconds)')

graph(W,'UpdateWaterContact','''(fn UpdateWaterContact ()
 (bind hero (Game|GetPlayerCharacter 0))
 (if (not (CallFunction|Valid :Object hero)) (return))
 (bind (x y z) (Math|Vector|BreakVector (Transformation|GetActorLocation :self hero)))
 (bind (vx vy vz) (Math|Vector|BreakVector (Transformation|GetVelocity :self hero)))
 (bind speed (Math|Float|Clamp(Float) (/ (+ (Math|Float|Max(Float) vx (- 0.0 vx)) (Math|Float|Max(Float) vy (- 0.0 vy))) 120.0) 0.0 1.0))
 (Rendering|Material|SetVectorParameterValue :Collection "'''+C+'''" :ParameterName "Contact" :ParameterValue (Math|Color|MakeColor x y z speed)))''')
if '(CallFunction|UpdateWaterContact)' not in code:code=code.replace('(CallFunction|ApplyDayNight)','(CallFunction|ApplyDayNight)\n  (CallFunction|UpdateWaterContact)')
graph(W,'EventGraph',code)
call('compile_blueprint',{'blueprint':ref(W),'warnings_as_errors':True})
call('save_assets',{'asset_paths':[W]},ASSET)
print('MOVEMENT_DRIVEN_LOCAL_WATER_CONTACT_SAVED')

