"""Temporary PIE setup for hands-on UI checks. Never save its actor in a map."""
from build_woodland_blockout import *
PREVIEW='/Game/Tests/World/BP_WoodlandUIPreview.BP_WoodlandUIPreview'
if __name__=='__main__':
    create(PREVIEW,'/Script/Engine.Actor')
    graph(PREVIEW,'EventGraph',f'''(event EventBeginPlay
 (Utilities|FlowControl|Delay 1.0)
 (for actor (Actor|GetAllActorsOfClass :ActorClass "{DIRECTOR}_C")
  (bind d (Utilities|Casting|CastToBP_CompanionCombat :Object actor)
   (:then
    (Utilities|Array|AddUnique (Class|BPCompanionCombat|GetRoster :self d) "Mossling")
    (Utilities|Array|AddUnique (Class|BPCompanionCombat|GetRoster :self d) "Rivercub")
    (Utilities|Array|AddUnique (Class|BPCompanionCombat|GetRoster :self d) "Moonmoth")
    (Class|BPCompanionCombat|SetActiveIndex :self d :ActiveIndex 2)
    (bind enemy (Game|SpawnActorfromClass :Class "{ENEMY}_C" :SpawnTransform (Math|Transform|MakeTransform :Location (Math|Vector|MakeVector 2300.0 0.0 100.0) :Scale (Math|Vector|MakeVector 0.5 0.5 0.5)) :CollisionHandlingOverride "AlwaysSpawn"))
    (Class|BPQuestEnemy|SetHealth :self enemy :Health 10000.0)
    (Class|BPQuestEnemy|SetMaximumHealth :self enemy :MaximumHealth 10000.0)
    (Class|BPQuestEnemy|SetAttackAt :self enemy :AttackAt 999999.0)) (:CastFailed))))''')
    call('save_assets',{'asset_paths':[PREVIEW]},ASSET)
