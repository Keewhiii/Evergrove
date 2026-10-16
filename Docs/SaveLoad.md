# Save and load

During gameplay, press F5 to quick-save and F9 to quick-load. Loading is manual; starting Play does not automatically overwrite or load a save. Close NPC dialogue and the quest journal first. The shortcuts display a short result message through PrintString in editor/development builds. A packaged Shipping build will need a UMG notification in place of that debug message; the save/load functions themselves use runtime Unreal APIs.

The single default slot is AdventureRPG_QuickSave, user index 0. In this editor project the file is Saved/SaveGames/AdventureRPG_QuickSave.sav. F5 replaces that slot. BP_Player.SaveSlotName can be changed for future multiple-slot menus. The test suite uses its own AdventureRPG_SaveValidation_20261009 slot and deletes only that test slot.

`Config/DefaultInput.ini` removes Unreal's inherited F5 Shader Complexity and F9
screenshot debug bindings so these keys only perform the game's save/load actions.
Restart the editor after changing this configuration; packaged games need a new
package. In an older running build, F3 restores normal Lit rendering if F5 has
switched the scene to white/black debug shading. Loading restores gameplay state,
not the viewport's debug rendering mode.

## Saved state

- Player transform, gold, active quest IDs, completed history, combat progress and inventory quantities.
- Remaining player-owned quest enemies and pickups: their quest IDs, objective kind/target, transforms, and enemy current/maximum health.
- Save version and level name for compatibility checks.
- Befriended summon roster (up to three), beasts met, selected summon, and player/companion health; see [CompanionCombat.md](CompanionCombat.md).
- World day number, full-precision minutes since midnight, day-cycle duration, and clock pause state. Loading restores these values exactly and refreshes sun/sky, lantern/window emission, and camera framing before returning to gameplay. No real-world/offline elapsed time is added.

The journal reads the restored player state on its next opening. Save/load never grants a quest reward. Completed enemies and consumed pickups are absent from the objective snapshot and are not recreated. Unrelated inventory quantities are preserved. The snapshot restores exact remaining actors rather than spawning a full fresh objective set from the catalog.

This version handles the current single-player, same-level prototype. It does not switch maps, serialize arbitrary world actors, or persist manually placed objectives without a QuestOwner. It rejects incompatible versions, different levels, missing catalog quests, invalid quantities and malformed objective snapshots without applying them. Catalog quest IDs and objective metadata must remain stable for an existing save to load. Unknown future versions require a migration before they can load.

Clock data is an additive extension of save version 1. `HasWorldClock` defaults
to false for older saves. They still load normally and leave the current clock
unchanged, because their historical save time was never recorded. Saving again
in the woodland records its clock. New sessions still start at 08:00 until the
player chooses F9 to load; loading a new-format save restores its recorded time.

## Implementation

BP_PlayerSave in Content/Game/Save inherits Unreal SaveGame. BP_Player.CapturePlayerSave builds a new value snapshot, and SaveProgress writes it through SaveGameToSlot. LoadProgress uses DoesSaveGameExist and LoadGameFromSlot, checks its class, and validates before restoring. RestorePlayerSave stages new objective actors with no QuestOwner, verifies spawning/teleporting, removes the former owned actors, copies player state, then assigns ownership to the replacements. Failed staging removes the new actors and keeps current quest state. Movement stops on successful load.

`Scripts/author_clock_save.py` adds `CaptureClockForSave`, `RestoreClockFromSave`
and `ValidateWorldClockSnapshot` to BP_Player, plus `CaptureWorldClock` and
`RestoreWorldClock` on BP_WoodlandWorld. The saved clock uses the same native
floating-point type as the live clock, with no conversion to displayed hours or
rounded minutes. Validation rejects invalid minute/day/rate values before
player restoration begins. The world restore recomputes derived clock values
with Delta=0, applies day/night lighting for the restored location, and updates
the camera immediately. The normal world tick then resumes from that time.

F5 and F9 were added as separate Pressed event connections in BP_Player.EventGraph; existing movement, interaction and journal graph connections were preserved. SaveProgress/LoadProgress return success booleans and update LastSaveLoadMessage and LastSaveLoadSucceeded so a future menu can call them directly. CanSaveLoad blocks requests while NPC dialogue or the journal is open. No level, NPC, quest bank or catalog changes are required for persistence.

Graph exports and validation logs are in Saved/SaveGameAudit. The player asset before this change is backed up there as BP_Player_before.uasset. Gameplay assets were authored, compiled and saved through Unreal editor APIs.

## Validation

BP_SaveGameValidation in Content/Tests/SaveGame runs two phases. With LoadOnly=false, it uses an isolated slot, tests a missing save, writes a real disk save, mutates live player/world state and loads it twice. It checks gold, quest IDs, inventory, combat progress, player/actor transforms, enemy health, remaining objectives, compatibility rejection and the journal guard. Stop Play, set the placed validator's LoadOnly=true, then start a fresh Play session. The second phase loads the prior disk save, repeats the state checks, kills the restored enemy, collects restored pickups, turns in both quests, checks rewards and duplicate-reward prevention, reloads, and deletes the test slot.

Both phases passed with SAVE_ROUNDTRIP_FAILURES=0 and SAVE_FRESH_SESSION_FAILURES=0. There were no Blueprint runtime errors. Production and test Blueprints compiled with warnings treated as errors. The temporary validator actor was removed and the level was not saved with it. Physical F5/F9 input remains a manual check; the runtime tests invoked the same save/load functions directly.

Clock continuity validation (`Scripts/validate_clock_save.py`) passed actual
SaveProgress/LoadProgress disk I/O and a separate fresh PIE session, using only
`AdventureRPG_ClockContinuityValidation_20261015`. Both restored day 7 at exactly
1163.4567890123 minutes with an 1800-second cycle and a running clock; subsequent
samples advanced normally. It also checks paused restoration, fractional
midnight rollover, immediate lantern/night state, legacy-shaped snapshots, and
malformed clock rejection without partial state changes. Gold restoration is
checked alongside the clock. Results are in `Saved/ClockSaveAudit/runtime.json`.
The temporary probe is removed, and the player's original slot name is restored.
The dedicated validation save is retained for inspection; production saves are
not overwritten. Existing physical F5/F9 routing is unchanged.

Manual check: accept delivery, combat and collection quests, partially complete them, press F5, then change position/progress/gold. Press F9 and verify the saved state returns. Stop and restart Play, press F9 again, and verify enemies, pickups and journal progress. Finish the restored quests and verify one reward per completion.
