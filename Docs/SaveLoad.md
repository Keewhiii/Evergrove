# Save and load

During gameplay, press F5 to quick-save and F9 to quick-load. Loading is manual; starting Play does not automatically overwrite or load a save. Close NPC dialogue and the quest journal first. The shortcuts display a short result message through PrintString in editor/development builds. A packaged Shipping build will need a UMG notification in place of that debug message; the save/load functions themselves use runtime Unreal APIs.

The single default slot is AdventureRPG_QuickSave, user index 0. In this editor project the file is Saved/SaveGames/AdventureRPG_QuickSave.sav. F5 replaces that slot. BP_Player.SaveSlotName can be changed for future multiple-slot menus. The test suite uses its own AdventureRPG_SaveValidation_20261009 slot and deletes only that test slot.

## Saved state

- Player transform, gold, active quest IDs, completed history, combat progress and inventory quantities.
- Remaining player-owned quest enemies and pickups: their quest IDs, objective kind/target, transforms, and enemy current/maximum health.
- Save version and level name for compatibility checks.

The journal reads the restored player state on its next opening. Save/load never grants a quest reward. Completed enemies and consumed pickups are absent from the objective snapshot and are not recreated. Unrelated inventory quantities are preserved. The snapshot restores exact remaining actors rather than spawning a full fresh objective set from the catalog.

This version handles the current single-player, same-level prototype. It does not switch maps, serialize arbitrary world actors, or persist manually placed objectives without a QuestOwner. It rejects incompatible versions, different levels, missing catalog quests, invalid quantities and malformed objective snapshots without applying them. Catalog quest IDs and objective metadata must remain stable for an existing save to load. Unknown future versions require a migration before they can load.

## Implementation

BP_PlayerSave in Content/Game/Save inherits Unreal SaveGame. BP_Player.CapturePlayerSave builds a new value snapshot, and SaveProgress writes it through SaveGameToSlot. LoadProgress uses DoesSaveGameExist and LoadGameFromSlot, checks its class, and validates before restoring. RestorePlayerSave stages new objective actors with no QuestOwner, verifies spawning/teleporting, removes the former owned actors, copies player state, then assigns ownership to the replacements. Failed staging removes the new actors and keeps current quest state. Movement stops on successful load.

F5 and F9 were added as separate Pressed event connections in BP_Player.EventGraph; existing movement, interaction and journal graph connections were preserved. SaveProgress/LoadProgress return success booleans and update LastSaveLoadMessage and LastSaveLoadSucceeded so a future menu can call them directly. CanSaveLoad blocks requests while NPC dialogue or the journal is open. No level, NPC, quest bank or catalog changes are required for persistence.

Graph exports and validation logs are in Saved/SaveGameAudit. The player asset before this change is backed up there as BP_Player_before.uasset. Gameplay assets were authored, compiled and saved through Unreal editor APIs.

## Validation

BP_SaveGameValidation in Content/Tests/SaveGame runs two phases. With LoadOnly=false, it uses an isolated slot, tests a missing save, writes a real disk save, mutates live player/world state and loads it twice. It checks gold, quest IDs, inventory, combat progress, player/actor transforms, enemy health, remaining objectives, compatibility rejection and the journal guard. Stop Play, set the placed validator's LoadOnly=true, then start a fresh Play session. The second phase loads the prior disk save, repeats the state checks, kills the restored enemy, collects restored pickups, turns in both quests, checks rewards and duplicate-reward prevention, reloads, and deletes the test slot.

Both phases passed with SAVE_ROUNDTRIP_FAILURES=0 and SAVE_FRESH_SESSION_FAILURES=0. There were no Blueprint runtime errors. Production and test Blueprints compiled with warnings treated as errors. The temporary validator actor was removed and the level was not saved with it. Physical F5/F9 input remains a manual check; the runtime tests invoked the same save/load functions directly.

Manual check: accept delivery, combat and collection quests, partially complete them, press F5, then change position/progress/gold. Press F9 and verify the saved state returns. Stop and restart Play, press F9 again, and verify enemies, pickups and journal progress. Finish the restored quests and verify one reward per completion.
