from build_companion_combat import *
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
code='''(fn MigrateLegacyVillageRoom ()
 (if (not (Utilities|String|EqualExactly(String) (Game|GetCurrentLevelName :bRemovePrefixString true) "L_EvergroveStart")) (return))
 (bind hero (Game|GetPlayerCharacter 0))
 (if (not (CallFunction|Valid :Object hero)) (return))
 (bind (x y z) (Math|Vector|BreakVector (Transformation|GetActorLocation :self hero)))
 (if (or (>= y -5000.0) (< y -15000.0)) (return))
 (if (> y -9700.0) (Transformation|SetActorLocation :self hero :NewLocation (Math|Vector|MakeVector x (- y 13400.0) 110.0) :bTeleport true) (return))
'''
for i in range(7):code+=f'(if (and (>= x {i*1550-775}.0) (< x {i*1550+775}.0)) (Transformation|SetActorLocation :self hero :NewLocation (Math|Vector|MakeVector (+ (- x {i*1550}.0) {(i+1)*12000}.0) (- y 23400.0) 110.0) :bTeleport true))\n'
graph(W,'MigrateLegacyVillageRoom',code+')')
code=(ROOT/'Saved/CombatAudit/UpdateCamera.dsl').read_text().replace('y -3000.0 3000.0','y -5100.0 3800.0')
if '(CallFunction|MigrateLegacyVillageRoom)' not in code:code=code.replace('(CallFunction|ResumeMapTravel)','(CallFunction|ResumeMapTravel)\n (CallFunction|MigrateLegacyVillageRoom)')
graph(W,'UpdateCamera',code,[('Delta','float',None)]);call('compile_blueprint',{'blueprint':ref(W),'warnings_as_errors':True});call('save_assets',{'asset_paths':[W]},ASSET)
