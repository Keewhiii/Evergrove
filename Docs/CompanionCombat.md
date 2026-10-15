# Relaxed companion combat

The prototype supports **three befriended summons, all active in combat, with one
selected follower while exploring**. It has no stamina, mana, combos, equipment statistics or
elemental weaknesses. Existing movement, dialogue, quests, journal and F5/F9
save/load controls remain in use.

## Controls

| Key | Action |
| --- | --- |
| E | Meet a wild beast, gather a treat, or offer treats to befriend it |
| 1 / 2 / 3 | Choose the overworld follower; in combat, choose who follows afterward |
| Left mouse | Attack the closest enemy in weapon range |
| V | Switch between sword and frost bolt |
| Q | Command the party to attack the nearest threat |
| H | Heal the player and shared companion health |
| Backspace | Release the selected companion outside combat and free its roster slot |

Movement and targeting use the existing single-player prototype. Left mouse is
one attack per press, subject to its cooldown; there is no aiming reticle or combo.
Combat and healing pause while dialogue or the journal is open.

## Combat display

The combat HUD takes its party-panel hierarchy from Tales of Symphonia and its
action diamond from Tales of Arise, using the project's existing woodland atlas:
warm parchment, leafy gold borders, illustrated companion portraits and dark
brown text that complement the dialogue and quest book.

Exploration normally shows only three numbered roster portraits. Player HP
appears for four seconds after health changes or healing is used; afterward it
hides above 50 HP, or becomes a small portrait/HP reminder at 50 HP or below.
A green underline identifies the chosen follower; empty slots show a plus.
Combat always shows the player and shared party health cards, marks all occupied slots, and
shows the lower-right action diamond for the current sword/frost attack,
companion command, healing and weapon swap, with the existing keyboard/mouse
bindings. Attack and healing show cooldown feedback; healing has a recharge
strip. A recovering party gets a status label. Temporary parchment notifications
sit at the top, leaving the middle of the view open. The persistent keybind banner
has been removed. Controls are game keys pressed with the Play/game viewport
focused, rather than commands typed in a terminal.

Summon rings and their centered number badges form a symmetric row beneath the
status panel. Player health cards use the actual front-facing player sprite as
a portrait inside the woodland frame, rather than the heart emblem. Party health
retains its paw emblem. Cards have centered labels measured by
Unreal's font metrics, and thin bordered health fills with a subtle highlight.
The health fill is inset inside the parchment. The alignment pass was inspected
in PIE with full/reduced HP and empty/occupied slots in both HUD modes; the
empty-roster close-up is `Saved/CombatAudit/HUD_Alignment_Detail.png`.

Visibility is cosmetic and lives in the HUD: transient samples of player health
and the healing cooldown timestamp refresh a four-second display timer. Damage,
healing, saved health and encounter timing are unchanged. The portrait samples
the face/shoulders from the existing `chibi_idle_UE5_2048x1024_exact_grid` texture;
no replacement character artwork or additional imported texture is required.
The timed PIE visibility preview exercised actual damage (100 to 65 to 40 HP)
and healing (40 to 75 HP). Eight captures confirmed the initial hidden state,
temporary full panels, timeout hiding, the compact low-health reminder and the
combat portrait. Evidence is `Saved/CombatAudit/Health_*.png`; the session had no
Blueprint runtime errors. Temporary preview actors were removed without saving
the level or a player save.

Layout scales against a 1280 by 720 reference with a 1.25 scale cap. Bottom and
right anchors follow the viewport, including wider aspect ratios. The HUD hides
while dialogue or the quest book prevents combat input. The style is authored
by `Scripts/style_combat_ui.py`; gameplay and input are unchanged.

Both modes compiled with warnings treated as errors. A timed PIE preview checked
exploration with one follower, entering combat with all three, and returning to
the chosen follower after the last enemy disappeared. Captures are
`Saved/CombatAudit/Party_Exploration.png`, `Party_Combat.png` and
`Party_AfterCombat.png`. The persistent keybind banner is absent in every mode.
Temporary preview actors were removed and their Blueprint graph restored; no
level or player save was saved by the preview.

## Befriending

Four training beasts spawn near the starting player: Mossling, Emberfox, Rivercub
and Moonmoth. They share the same combat abilities in this first version and have
distinct colors and labels. Meet a beast with E, gather two treats from the small
gold cubes, then return and press E again. This short gathering request adds it to
the roster and attempts to summon it. Treats regrow after 25 seconds.

Full rosters reject a fourth beast without consuming treats. A beast already in
the roster cannot be added twice. Outside combat, Backspace releases the selected beast;
it can be befriended again later for two treats. Released roster entries shift
forward to fill the gap. Summon switching has a two-second cooldown and shares
companion health, so switching does not provide free healing.

These training actors spawn at runtime; no permanent level layout was replaced.

## Combat and recovery

- A live quest enemy within 850 units starts combat. While fighting, threats
  within 1050 units keep combat active. Four seconds without a nearby threat
  returns the HUD and summons to exploration mode. Dialogue and the quest book
  pause encounter updates along with combat input.
- Every roster entry is summoned in combat (up to three); outside combat only
  the selected follower remains. Each beast has its own 0.8-second attack timer
  and deals one damage per hit through the player's quest damage/reporting path.
  Q selects the nearest enemy within 950 units for the party.
- Sword attacks deal three damage within 190 units, with a 0.8-second cooldown.
  Frost bolts deal four damage within 750 units, with a 1.4-second cooldown.
- During combat, enemies approach at 95 units/second within 1050 units, wind up for one second,
  and then attack nearby targets. They turn gold while winding up. Attacks have a
  two-second recovery; moving away avoids the hit. Player hits deal eight damage;
  companion hits deal ten. A shared 0.8-second hurt cooldown limits crowd damage.
- Player health is 100; companion health is 60. H restores 35 and 25 respectively,
  capped at maximum, with an eight-second cooldown.
- Companion health remains a shared 60-point pool. A knocked-out party retreats
  for 15 seconds, then returns healed: all three in combat or the selected follower
  in exploration. Switching slots cannot bypass recovery. Player defeat returns the player to the
  session's starting safe transform with full health and five seconds of protection.
  Inventory, gold and quest progress are retained.

Quest enemies no longer take damage from E. Use left mouse or a companion. Their
existing damage function still rejects nonpositive damage, reports only lethal
defeats, and prevents repeat credit. Collection and delivery behavior is retained.

## Persistence

The existing save snapshot includes the roster, beasts already met, selected
roster slot, player health and shared companion health. Loading clears all old
party actors and resumes exploration with at most one follower; the next encounter
update may re-enter combat if a restored threat is nearby. Actor references,
encounter state and individual attack timers are transient. A saved knocked-out party resumes
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

`Scripts/author_party_combat.py` migrates encounter state, three simultaneous
summons, follower switching and party cleanup while retaining the save schema.
Run it after the original prototype migrations, then `Scripts/style_combat_ui.py`.
Re-running the older runtime migration alone would restore the single-summon behavior.

The Python files in `Scripts/*companion*.py` and `Scripts/*party*.py` are explicit editor authoring and
validation tools, not runtime dependencies. They require the local Unreal MCP
editor and existing authoring audit helpers. Runtime graphs and prior graph
exports are in `Saved/CombatAudit`; those generated files are untracked. Do not run
these migrations automatically at game startup. All binary assets were authored
through Unreal editor tools.

## Validation and current limits

`Scripts/validate_party_combat.py` authors `BP_PartyCombatValidation`. All 32
checks passed in PIE with `PARTY_FINAL_FAILURES=0`, covering follower replacement,
combat entry/exit and grace, three active species, independent attacks/cooldowns,
quest credit, shared knockout/recovery, enemy attacks against secondary summons,
healing, player defeat, isolated disk save/load and duplicate-free restoration.
The report is `Saved/CombatAudit/PartyValidation.log`. The test used and deleted
only `AdventureRPG_PartyValidation_20261014`; the production quick-save was not
written. No Blueprint runtime errors appeared in the validation/preview sessions.
Physical keyboard input still needs a player smoke test.

The original single-companion `BP_CombatValidation` checked roster limits, taming costs, duplicate rejection,
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
