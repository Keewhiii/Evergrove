# World anchored wind — 2026-10-15

`BP_WoodlandWorld.UpdateVisibleWind` previously copied player X/Y on every camera
update, making the wind field move with the player. It now anchors the field at
(2000, 0, 0), spanning the hub and trail with the existing ribbon mesh and its
leftward material transport. The existing gust envelope and fluid curls remain.
Wind stays hidden inside the guild (player Y below -5000).

Both GameDefaultMap and EditorStartupMap now select `/Game/Maps/L_WoodlandBlockout`.

`Scripts/fix_world_anchored_wind.py` applies the Blueprint migration. The original
wind authoring script also uses the fixed anchor so regeneration retains the fix.
`Scripts/validate_world_anchored_wind.py` passed in PIE: the camera moved over
1000 cm while wind remained fixed; guild entry/exit hid and restored wind.
Successive rendered frames show moving ribbons. Evidence is stored in
`Saved/WoodlandWindFXAudit/world_anchored_runtime.json` and `WorldAnchoredWind_*.png`.

The updated Windows game is packaged into `Saved/BaselinePackage/Windows`.
Launch `AdventureRPG.exe` there; keep its accompanying folders and pak files.
