# First woodland outing

Play `/Game/Maps/L_WoodlandBlockout`. The guild and first clearing now have an
additive environment pass: timber window panels, a woven-style rug, desk books,
benches, terracotta planters, lantern posts, shrubs, flowers and stepping stones.
These use native meshes and the existing soft woodland palette. They are a
first art pass; the surrounding map still uses blockout geometry.

After completing the original Luna-to-Rein delivery, request work from Luna:

1. **A Little Warmth — Tea for the Guild:** collect three meadow mint sprigs
   beside the east trail and return to Luna for 20 gold.
2. **A Little Warmth — A Peaceful Path:** request again, defeat three bramble
   pests in the first clearing, and return to Luna for 40 gold.

The patrol remains unavailable until the tea is turned in. Both requests are
one-time quests and take priority over random commissions when eligible.
Existing completed-delivery saves can begin the outing immediately. The 200
repeatable commissions remain available. J shows the active request and progress.
E gathers mint; LMB attacks. The existing summon and battle systems apply.

The dressing is generated once per play session by BP_CozyWoodland, spawned by
BP_WoodlandWorld. This makes it persistent through saved Blueprint assets without
adding World Partition external actor packages. It appears when playing; the
editor map retains its blockout view. All new dressing has no collision, leaving
the existing navigation obstacles authoritative. Quest targets use the existing
objective/save systems and are grouped in the first clearing for this outing.

Authoring: `Scripts/build_cozy_outing.py`. Isolated tests:
`Scripts/validate_cozy_outing.py` and `Scripts/run_cozy_checks.py`.
The test snapshots and restores player state and never writes the player's save.
All 11 introductory quest checks passed, including prerequisites, request order,
real collection/defeat progress, correct turn-in NPC, exact payouts, duplicate
reward prevention and one-time completion. Visual captures were reviewed in
`Saved/CombatAudit/Cozy_Guild.png` and `Cozy_Clearing.png`.

Regression checks also passed: 32 woodland, 32 party and 30 trail AI checks,
for 105 passing runtime checks including the new outing. The party suite must
start outside the safe hub; an initial run at PlayerStart was rejected by the
hub's intended combat protection. The corrected runner supplies a trail start.
Evidence: `Saved/CombatAudit/CozyRegressionResults.json` and editor log entries
`COZY_FINAL_FAILURES=0`. Temporary test actors were removed, PIE stopped, and
the level retained its 79 original tagged actors. No new external actor save
step is required for this environment pass.

The Windows package was rebuilt successfully on October 15, 2026 (BuildCookRun
41.07 seconds, exit code 0). Launch
`Saved/BaselinePackage/Windows/AdventureRPG.exe`. In-game visuals were verified
in PIE; standalone startup was not separately checked in this pass.
