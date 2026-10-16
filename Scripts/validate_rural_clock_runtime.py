"""Run the existing clock probe in the new map and preserve its legacy fixture."""
from build_companion_combat import *
import time
T='/Game/Tests/World/BP_ClockSaveValidation.BP_ClockSaveValidation'
W='/Game/Game/World/BP_WoodlandWorld.BP_WoodlandWorld'
APP='EditorToolset.EditorAppToolset';ACT='editor_toolset.toolsets.actor.ActorTools'
OUT=ROOT/'Saved/RuralClockSaveAudit';OUT.mkdir(exist_ok=True)
slot=ROOT/'Saved/SaveGames/AdventureRPG_ClockContinuityValidation_20261015.sav'
backup=slot.read_bytes()
try:
 source=(ROOT/'Scripts/validate_clock_save.py').read_text()
 exec(source[source.index("probe=call('add_to_scene_from_asset'"):])
finally:
 slot.write_bytes(backup)
