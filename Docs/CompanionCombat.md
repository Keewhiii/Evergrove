# Relaxed companion combat

The prototype supports **three befriended summons in the roster, with one active
companion at a time**. It has no stamina, mana, combos, equipment statistics or
elemental weaknesses. Existing movement, dialogue, quests, journal and F5/F9
save/load controls remain in use.

## Controls

| Key | Action |
| --- | --- |
| E | Meet a wild beast, gather a treat, or offer treats to befriend it |
| 1 / 2 / 3 | Summon the corresponding roster entry |
| Left mouse | Attack the closest enemy in weapon range |
| V | Switch between sword and frost bolt |
| Q | Command the companion to attack the nearest threat |
| H | Heal player and companion |
| Backspace | Release the selected companion and free its roster slot |

Movement and targeting use the existing single-player prototype. Left mouse is
one attack per press, subject to its cooldown; there is no aiming reticle or combo.
Combat and healing pause while dialogue or the journal is open.

## Combat display

The combat HUD uses the existing woodland dialogue frame, parchment panels and
dark brown text to match the dialogue and quest journal. It shows player and
companion health bars, three numbered summon slots, a green marker on the selected
slot, the equipped weapon on the frame's nameplate, and keyboard hints. Temporary
messages appear in a separate matching parchment strip. Layout scales down for
smaller viewports and stays at its designed size on large screens. The style is
authored by `Scripts/style_combat_ui.py`; gameplay and input are unchanged.
The HUD Blueprint compiled with warnings treated as errors, and its parchment,
health bars, occupied/empty slots and notification layout were inspected in PIE
(`Saved/Screenshots/WindowsEditor/ScreenShot00009.png`).

## Befriending

Four training beasts spawn near the starting player: Mossling, Emberfox, Rivercub
and Moonmoth. They share the same combat abilities in this first version and have
distinct colors and labels. Meet a beast with E, gather two treats from the small
gold cubes, then return and press E again. This short gathering request adds it to
the roster and attempts to summon it. Treats regrow after 25 seconds.

Full rosters reject a fourth beast without consuming treats. A beast already in
the roster cannot be added twice. Backspace releases the currently selected beast;
it can be befriended again later for two treats. Released roster entries shift
forward to fill the gap. Summon switching has a two-second cooldown and shares
companion health, so switching does not provide free healing.

These training actors spawn at runtime; no permanent level layout was replaced.

## Combat and recovery

- The companion follows automatically and attacks threats within 850 units. Q
  selects the nearest enemy within 950 units. Companion hits deal one damage every
  0.8 seconds and use the owning player's existing quest damage/reporting path.
- Sword attacks deal three damage within 190 units, with a 0.8-second cooldown.
  Frost bolts deal four damage within 750 units, with a 1.4-second cooldown.
- Enemies approach at 95 units/second within 900 units, wind up for one second,
  and then attack nearby targets. They turn gold while winding up. Attacks have a
  two-second recovery; moving away avoids the hit. Player hits deal eight damage;
  companion hits deal ten. A shared 0.8-second hurt cooldown limits crowd damage.
- Player health is 100; companion health is 60. H restores 35 and 25 respectively,
  capped at maximum, with an eight-second cooldown.
- A knocked-out companion retreats for 15 seconds, then returns healed. Switching
  slots cannot bypass its recovery. Player defeat returns the player to the
  session's starting safe transform with full health and five seconds of protection.
  Inventory, gold and quest progress are retained.

Quest enemies no longer take damage from E. Use left mouse or a companion. Their
existing damage function still rejects nonpositive damage, reports only lethal
defeats, and prevents repeat credit. Collection and delivery behavior is retained.

## Persistence

The existing save snapshot now includes the roster, beasts already met, selected
roster slot, player health and companion health. Loading recreates at most one
active companion and clears stale targets. A saved knocked-out companion resumes
a fresh 15-second rest; healing resumes with an eight-second cooldown.

Existing version-1 saves receive empty-roster and healthy defaults for these new
fields. No production quick-save was intentionally overwritten by validation.
Oversized rosters, invalid selected indices, unknown roster species and health
outside the supported range are rejected before restoration.

## Assets and implementation

- `Content/Game/Combat/BP_CompanionCombat`: combat orchestration, roster and input.
- `Content/Game/Combat/BP_Beast`: beast/treat interaction and native mesh appearance.
- `Content/Game/Combat/BP_CombatHUD`: health, roster, controls and feedback.
- `Content/Game/Combat/M_*`: simple native prototype materials.
- `BP_Gamemode` creates the combat director and selects the combat HUD.
- `BP_Player` save capture/restore/validation and `BP_PlayerSave` serialize the new state.
- `BP_QuestEnemy` retains quest damage reporting and changes E interaction.

The Python files in `Scripts/*companion*.py` are explicit editor authoring and
validation tools, not runtime dependencies. They require the local Unreal MCP
editor and existing authoring audit helpers. Runtime graphs and prior graph
exports are in `Saved/CombatAudit`; those generated files are untracked. Do not run
these migrations automatically at game startup. All binary assets were authored
through Unreal editor tools.

## Validation and current limits

`BP_CombatValidation` checks roster limits, taming costs, duplicate rejection,
switching, attacks and cooldowns, enemy approach/windup/damage, healing, companion
retreat/return, gentle player defeat, companion quest credit, and snapshot/disk
save restoration. Its first phase reports `COMBAT_FAILURES=0`; a new PIE session
with its instance's LoadOnly enabled reports `COMBAT_FRESH_FAILURES=0`. It uses
only `AdventureRPG_CombatValidation_20261013` and deletes that test slot in phase two.
Temporary validators were removed without saving them into the level.

The original save tests also passed with `SAVE_ROUNDTRIP_FAILURES=0` and
`SAVE_FRESH_SESSION_FAILURES=0`. A game-view screenshot was inspected for HUD
placement and beast visibility. Physical input still needs a player smoke test;
the native Computer Use helper was unavailable in this session.

The original quest-bank suite passed delivery, combat, collection, rewards and
200 mixed replay cycles. Autonomous combat was disabled in that isolated fixture
run so it would not interfere with scripted objective actors; production combat
was re-enabled afterward. The new combat suite separately exercised autonomous
enemy steps and companion attacks with production combat enabled.

The final Windows Development package built successfully at
`Saved/PackagedSmoke/Windows/AdventureRPG.exe`. An unattended packaged startup
returned exit code zero and loaded the prototype map with combat enabled. The
smoke-test log is `Saved/CombatAudit/PackagedCombatSmoke.log`. Existing packaged
quick-save data was retained.

This is a playable foundation with simple mesh beasts. Attacks use immediate
damage and debug line feedback in Development builds; sword animation and a
traveling spell projectile are not implemented. Movement uses direct steering
with obstacle checks, not navigation/pathfinding. Companions can stop at obstacles
and catch up by teleporting when very far away. Training spawns are fitted to the
current room; this is not a general encounter-placement system. Treat regrowth and
individual training actors are not world-save snapshots.

Start the packaged game, befriend a beast, accept a combat quest from Luna, and
let the companion handle a target. Try sword/spell attacks and H, then turn in the
quest. Save, change roster/health, and load to check the restored companion.
