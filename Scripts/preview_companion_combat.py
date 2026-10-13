"""Temporary in-editor preview helper; never placed in the saved level."""
from build_companion_combat import *
PREVIEW='/Game/Tests/Combat/BP_CombatPreview.BP_CombatPreview'
if __name__=='__main__':
    create(PREVIEW,'/Script/Engine.Actor')
    graph(PREVIEW,'EventGraph',f'''(event EventBeginPlay
 (Utilities|FlowControl|Delay 1.0)
 (for actor (Actor|GetAllActorsOfClass :ActorClass "{DIRECTOR}_C")
  (bind director (Utilities|Casting|CastToBP_CompanionCombat :Object actor)
   (:then
    (Utilities|Array|AddUnique (Class|BPCompanionCombat|GetRoster :self director) "Mossling")
    (Class|BPCompanionCombat|SummonSlot :self director :Index 0)) (:CastFailed)))
 (Utilities|FlowControl|Delay 1.0)
 (Development|ExecuteConsoleCommand :Command "Shot showui" :SpecificPlayer (Game|GetPlayerController 0)))''')
