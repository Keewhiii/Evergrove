# Startup and Windows package smoke test

Verified 2026-10-13 with Unreal Engine 5.8.3, Windows Development configuration.

## Startup configuration

`Config/DefaultEngine.ini` sets both `GameDefaultMap` and `EditorStartupMap` to
`/Game/L_Prototype`. The map already overrides its game mode with
`/Game/Game/Characters/Player/Blueprints/BP_Gamemode.BP_Gamemode_C`.
That game mode's default pawn is `BP_Player`; no map or Blueprint edits were needed.

## Results

- PIE created a `BP_Player` instance using the map's game mode.
- Quest bank validation passed combat, collection, delivery, rewards and 200 mixed replay cycles.
- Quest journal validation reported `JOURNAL_FAILURE_COUNT=0`.
- Save validation reported `SAVE_ROUNDTRIP_FAILURES=0` and, in a new PIE session,
  `SAVE_FRESH_SESSION_FAILURES=0`.
- Temporary validation actors were removed. The map was not saved with them.
- Windows game compilation, cooking, staging, packaging and archiving succeeded.
- The packaged game was launched without a map argument using `-nullrhi -nosound
  -unattended -nosplash -seconds=8`. It returned exit code 0, loaded
  `/Game/L_Prototype`, selected `BP_Gamemode_C`, and initialized the engine.
  Its log contained no `Error:`, fatal error or `Accessed None` messages.

Evidence remains in `Saved/Logs/AdventureRPG.log` and
`Saved/Logs/PackagedStartupSmoke.log`. These are generated, untracked files.
The package is in `Saved/PackagedSmoke/Windows`; launch `AdventureRPG.exe` there.

## Repeat the package build

From the project directory in PowerShell:

```powershell
.\Scripts\package_smoke.ps1
# For another engine installation:
.\Scripts\package_smoke.ps1 -EngineRoot 'E:\UE5\UE_5.8'
```

The script uses the installed `UnrealEditor-Cmd.exe` for cooking. Rebuilding an
editor target failed because this machine lacks the .NET Framework SDK needed by
SwarmInterface. Using `-nocompileeditor` and an explicit `-unrealexe` allowed the
game build and package to succeed without changing engine or plugin settings.

An additional uncooked editor `-game` startup test loaded the correct map and
exited with code 0, but experimental editor tooling emitted Python startup errors
for missing `AgentSkill` and `PythonTestRunner` types. The packaged game did not
emit these errors.

## Remaining interactive checks

### Save/load key conflict corrected

The first interactive packaged run revealed that F5 also invoked Unreal's
inherited `viewmode shadercomplexity` debug binding. Its log recorded the view
switch and successful save together; F9 recorded a successful load while leaving
the debug view unchanged. The inherited F9 screenshot binding also conflicted.
`Config/DefaultInput.ini` now removes both entries. The Windows package was rebuilt
successfully, and a fresh packaged runtime dump of `EnhancedPlayerInput.DebugExecBindings`
confirmed that neither F5 nor F9 remains in that array. Evidence:
`Saved/Logs/SaveKeyBindingsSmoke.log`. The existing packaged quick-save file was
preserved. Physical input retesting remains pending.

The Windows Computer Use helper was unavailable (native pipe not found), so
physical keyboard input, rendered appearance and the complete interactive
packaged gameplay loop have **not** been verified. The unattended package test
disabled rendering and audio. Runtime validators called gameplay functions
directly; they do not prove keyboard routing or focus behavior.

1. Launch the packaged `AdventureRPG.exe`. Confirm the prototype scene and player
   appear; test movement and sprint.
2. Talk to Luna with E. Test W/S selection and wrapping across all five choices,
   request a quest, exit, and verify holding E does not repeat actions.
3. Complete a delivery at Rein, and combat/collection objectives at Luna using
   Turn in Quest Items. Check incomplete rejection and no duplicate reward.
4. Open J. Test W/S, arrow keys, Tab, Page Up/Down, J and Escape. Verify movement
   and NPC interaction resume after closing.
5. With dialogue/journal closed, partially complete quests and press F5. Change
   position/progress, press F9, and verify restoration. Restart the packaged game
   and press F9 again. Confirm remaining targets, health and journal progress.

The save tests used their isolated validation slot; the production quick-save
slot was not intentionally overwritten by these tests.
