# Woodland playable blockout

Open `/Game/Maps/L_WoodlandBlockout` in Unreal and press Play. The original
`/Game/L_Prototype` remains available as the editor startup map. The packaged
game now starts in the woodland map. This is a layout
blockout with simple colored geometry, not finished environment art.

The guild hub occupies X -1100 to 1100 and Y -1000 to 1000. The east trail leads
to three clearings. Combat and collection requests spawn their objectives in
those clearings rather than beside the receptionist. Entering the hub ends the
encounter immediately and cancels enemy windups. The hub uses its own save slot,
`AdventureRPG_WoodlandBlockout`; the original prototype save is untouched.

WASD supports eight directions at consistent speed. Shift retains the existing
sprint behavior. Four-direction sprites face the newly pressed axis on a
diagonal and keep that facing while both keys stay held. Horizontal animation
assets have reversed names, so the animation mapping compensates for that.
Interaction traces follow the displayed direction. A smooth camera follows the
player with fixed orientation and bounds suited to this area.

E interacts, J opens/closes the quest journal, F5 saves and F9 loads. See
[CompanionCombat.md](CompanionCombat.md) for attacks, healing and beast controls.
Click the Play viewport before using game keys. These are game inputs, not
terminal commands.

## Validation

On October 14, 2026, isolated PIE validation passed **32 woodland checks and 32
party checks**, with both final failure counts zero. Woodland checks cover eight
normalized directions, stable facing, left/right interaction, safe hub entry,
blocking an already winding-up enemy, trail objective spawning, combat and
collection turn-ins, and save/load restoring the trail position. Party checks
run on the new map outside the hub and cover one exploration follower, switching,
three battle summons, attacks, cooldowns, recovery, quest credit, and restore
without duplicate summons. These are runtime function checks, distinct from
physical keyboard testing.

Interactive checks completed October 15, 2026: E opens Luna's greeting and five
choices, accepts the starter delivery, and turns it in to Rein. J opens/closes
the journal. LMB produces an attack and cooldown feedback; V switches to frost
with one press; H shows healing feedback and cooldown; Q commands the party;
D displays the corrected right-facing sprite; 1 selects a different overworld
follower. The combat HUD displays the player portrait, health cards, three
summons and action diamond. Returning to the safe hub hides those combat panels
and restores one selected follower. Test positions and the three-member roster
were prepared through editor tools; keyboard/mouse actions used actual inputs.

This pass fixed copied NPC dialogue settings, reversed horizontal animation
mapping, and duplicate LMB/Q/H/V execution bindings (V previously toggled twice).
World Partition persistence was also fixed: Unreal Save All writes the external
actor packages. A round trip through the original map and back confirmed all 78
tagged blockout actors and Luna's text persist. The temporary UI/validation actors
were removed; no test roster or request was written to the player's save.

Evidence: `Saved/CombatAudit/WoodlandValidationResults.json` and the corresponding
`WOODLAND_FINAL_FAILURES=0` / `PARTY_FINAL_FAILURES=0` editor log entries.
Authoring scripts live in `Scripts/build_woodland_blockout.py`,
`connect_woodland_gameplay.py`, and `polish_exploration_movement.py`.
`validate_woodland.py` authors the isolated test Blueprint.
After rebuilding the scene, use Unreal **Save All (Ctrl+Shift+S)** before leaving
the map. Saving only the .umap through the asset API does not save newly created
external actors; the MCP `save_actor` helper rejects those new packages until
their initial Save All. `fix_combat_input_bindings.py` keeps one live input
execution path per combat key and is called by the original runtime authoring
script to make repeated migrations safe.

The updated Windows package was built October 15, 2026, with BuildCookRun exiting
successfully (exit code 0). Its executable is
`Saved/BaselinePackage/Windows/AdventureRPG.exe`; the folder name is retained from
the earlier baseline build. GameDefaultMap is now `/Game/Maps/L_WoodlandBlockout`.
Computer Use launch approval timed out, so packaged startup has not yet been
visually verified. The editor playtest and reload checks above are separate.
See [Playtest.md](Playtest.md) for the player checklist. The subsequent AI pass
adds cached navigation paths, enemy leashes, attack-radius markers and floating
damage numbers; see [TrailAI.md](TrailAI.md). That pass has 94 passing runtime
checks and a successful updated package. Ordinary routing goes around obstacles;
the 1600-unit exploration catch-up teleport remains a recovery measure.
