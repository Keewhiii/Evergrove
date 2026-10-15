# Woodland navigation and enemy behavior

Companions and enemies now use a cached, complete Unreal navigation path in the
woodland level. Routes update every 0.8 seconds or when their destination moves
140 units. Movement follows path corners with collision sweeps. Invalid or
partial routes stop safely. The original prototype retains traced direct
movement because it has no navigation bounds. The existing 1600-unit exploration
catch-up teleport remains a recovery measure, separate from ordinary routing.

Enemies remember their first encounter position as home. Moving the player more
than 900 units from home, leaving combat, or entering the safe guild hub cancels
their attack and sends them home at 180 units/second. They cannot be retargeted
while returning and resume encounters within 60 units of home. Returning does
not restore enemy health. Home positions are transient and are initialized from
restored actor positions after loading; the existing save schema is unchanged.

The existing one-second enemy windup shows a translucent gold disk with a
170-unit attack radius. Leaving that radius before resolution avoids the hit.
The marker disappears when the attack resolves or is cancelled. Damage amounts
and party recovery rules remain unchanged. Hits briefly brighten the enemy and
spawn a warm-colored floating damage number for 0.65 seconds, including on a
lethal hit. Quest credit still runs through the original damage function.

Navigation bounds cover the hub and trail. Tree trunks, rocks and fences remain
obstacles. Canopies and thin path/clearing overlays explicitly disable the mesh
default collision profile, collision and navigation relevance. This avoids
canopies blocking the gate route at navigation-agent height.

## Validation and persistence status

The isolated `BP_TrailAIValidation` checks the actual map geometry: complete
routes around a tree, rock and hub fence; arrival without teleporting; safe
unreachable routes; home/leash behavior; warning visibility and dodge timing;
unchanged damage; hit-number placement and feedback surviving lethal damage.
The final AI run has zero failures. The existing 32 woodland checks and 32 party
checks were rerun afterward and also have zero failures.

All 94 runtime checks passed (30 AI, 32 woodland, 32 party), and temporary
validation actors have been removed. The user saved the external actors with
Unreal Save All. A full map reload confirmed 79 tagged actors, the navigation
bounds, dynamic Recast generation, and disabled decorative collision/navigation.

Unreal's own screenshot command supplied visual QA after desktop window
activation failed. The attack-radius marker, hit flash and floating damage
number were inspected in PIE. Damage numbers were enlarged to 64 world units
and dark brown for contrast. Evidence is `Saved/CombatAudit/Trail_Warning.png`
and `Trail_Hit.png`. The preview held one enemy in a stationary windup; timing,
cancellation and damage behavior were covered by the runtime checks separately.

The updated Win64 Development package completed successfully on October 15,
2026 (BuildCookRun exit code 0, 58.37 seconds). Open
`Saved/BaselinePackage/Windows/AdventureRPG.exe`. Packaged visual startup has not
been inspected; the visual captures above came from PIE.

`Scripts/configure_trail_navigation.py` reapplies the external actor setup if
needed, without rebuilding the map. `improve_trail_ai.py` authors runtime logic,
and `validate_trail_ai.py` authors the tests. Do not rerun older combat migrations
over these functions. See `Saved/CombatAudit/TrailAIResults.json` for validation
and package status.
