# Quest Bank

## Implemented behavior

BP_QuestBank and BP_QuestItemRule are Blueprint subclasses of **PrimaryDataAsset**. DA_QuestBank references the existing DT_Quests catalog. BP_Player defaults to this bank and retains its existing ActiveQuestIDs and CompletedQuestIDs as the authoritative player state.

NPCs retrieve available quests by stable QuestNPCID, falling back to NPCName when that ID is None. Catalog size is unrestricted by the NPC graphs. Eligible quest IDs are sorted lexically for stable queries. Requests offer eligible one-time quests first, then use a weighted random draw among repeatable quests. There is no new quest-selection UI.

An active quest reserves its configured SharedItemTypes. These are item-type identifiers, not individual inventory instances. An intersection with another active quest blocks acceptance; unrelated quests remain available. Completion releases reservations. Active quests cannot be accepted again. Completed one-time quests remain excluded; completed repeatable quests become eligible again. ItemRules is a map keyed by the exact quest ID string, allowing direct rule lookup.

The existing Luna-to-Rein delivery is catalog row 0_Delivery_001. Its original request, completion and thank-you text are preserved. NPC interaction completes all active quests targeting that NPC using a snapshot, so removing completed IDs does not skip another quest. Existing dialogue choices, closing behavior and E-repeat protection are retained. Older hard-coded quest nodes and fields remain disconnected rather than deleted.

## Add a quest in Unreal Editor

1. Open Content/Game/Quests/Blueprints/DT_Quests. Add a row with a unique stable name, for example Luna_Delivery_002.
2. Set questId to exactly the row name. Fill questName, description (the acceptance dialogue), objectiveText, difficulty, rewardGold and requiredAmount.
3. Set questGiver to the giving NPC's QuestNPCID. If QuestNPCID is None, use its NPCName. Set targetNPC to the receiving NPC's corresponding identifier. For the existing actors these are Luna and Rein. Set targetNPC to Luna for Combat/Collection; delivery rows use their actual recipient (currently Rein).
4. Save the table. This alone is sufficient for a quest that does not reserve any shared item types. Luna's Blueprint needs no edits.
5. For a shared-item quest, right-click in Content/Game/Quests, select Miscellaneous > Data Asset, choose BP_QuestItemRule, and name the asset. This class inherits PrimaryDataAsset.
6. Open the rule asset. Set QuestID to the row ID. Add Name entries to SharedItemTypes, such as GuildDeliveryPackage. Use the same type identifier in every quest that must conflict. None entries are ignored.
7. Optionally fill CompletionText and CompletedText for the turn-in response and subsequent thank-you. Empty values use generic responses.
8. Open DA_QuestBank. Add an ItemRules map entry whose string key is the exact row ID and whose value is the rule asset. Save both assets. Keep the rule QuestID equal to the map key.
9. For a new NPC, set its QuestNPCID to a stable unique Name, or use its NPCName fallback. Enable CompletesQuestOnInteract for a receiving NPC. An eligible quest enables dialogue choices automatically; an NPC's existing HasChoices also continues to apply.

Keep quest IDs, NPC IDs and item-type metadata stable while quests are active. Removing a catalog row prevents that quest from turning in. There is no fixed quest count or one-active-quest limit.

## Scope

No inventory system was found in this project. Shared types express quest reservations. Delivery keeps its existing talk-to-target behavior; combat and collection use requiredAmount as an enforced objective count. Collection pickups are consumed into quest progress, with no general inventory added. BP_Player.Gold now receives rewardGold on a successful turn-in. No gold HUD or save-game persistence is added. Catalog rows use the existing ST_QuestData rather than a duplicate schema.

## Validation and editor tests

Runtime validation passed with banks containing 3, 30 and 300 quests. It checked eligibility, multiple active quests, shared-type conflicts, duplicate and completed-ID rejection, wrong targets, completion of multiple quests without skipping, reservation release, and production Luna/dialogue/Rein integration. Blueprint compilation passed with warnings treated as errors. No Blueprint runtime errors were reported in the validation run.

The reusable fixtures live in Content/Tests/QuestBank and are not connected to the production bank. To repeat validation, temporarily place BP_QuestBankValidation in L_Prototype, press Play, and inspect Output Log for QUEST_BANK_VALIDATION_PASS or QUEST_BANK_VALIDATION_FAIL. It restores the player's original active/completed arrays after its checks. Stop Play and remove the temporary actor. The implementation's temporary validator actor has already been removed; the level was not saved.

Manual interaction checks:

1. Play L_Prototype with no active/completed delivery. Talk to Luna and choose the quest request. Verify the original request text and one active 0_Delivery_001 entry.
2. Add a second Luna-to-Rein table row with no shared types. Request again while the delivery is active; both quests should be active.
3. Add a third quest with GuildDeliveryPackage reserved through its item rule. It should be unavailable while the original delivery is active.
4. Talk to Rein. Both eligible active quests should complete once, and the original delivery completion text should appear. Request again from Luna; the shared-type quest should now be available, while completed quests stay unavailable.
5. Talk to Rein again and check the original thank-you with the original delivery alone completed. With multiple completed quests, the most recent quest targeting Rein supplies the thank-you.
6. Exercise guild/advice/exit choices, hold E, close and reopen dialogue, and verify no repeated advances or stacked dialogue widgets.

## Changed files

Modified existing assets:

- Content/Game/Characters/Player/Blueprints/BP_Player.uasset ? bank reference; existing player quest arrays reused.
- Content/Game/Characters/NPCs/BP_Npc.uasset ? dynamic NPC lookup, quest completion and resolved dialogue wiring.
- Content/Game/Characters/NPCs/WBP_Dialogue.uasset ? quest-request choice routed through the bank.
- Content/Game/Quests/Blueprints/DT_Quests.uasset ? migrated existing delivery row.

New production assets:

- Content/Game/Quests/Blueprints/BP_QuestBank.uasset
- Content/Game/Quests/Blueprints/BP_QuestItemRule.uasset
- Content/Game/Quests/DA_QuestBank.uasset
- Content/Game/Quests/DA_DeliveryItemRule.uasset

New test assets in Content/Tests/QuestBank:

- BP_QuestBankValidation.uasset
- DA_ConflictItemRule.uasset
- DT_QuestBank_3.uasset, DT_QuestBank_30.uasset, DT_QuestBank_300.uasset
- DA_QuestBank_3.uasset, DA_QuestBank_30.uasset, DA_QuestBank_300.uasset

Text files: Docs/QuestBank.md and Scripts/quest_bank_mcp.py (editor audit helper; requires the current Saved MCP audit/session files). Backups, graph exports, construction scripts and validation logs are in Saved/QuestBankAudit.

All binary asset changes were performed through Unreal MCP/editor. No C++ or configuration changes were made for the Quest Bank. Existing project/plugin configuration changes were left intact. Blueprints and data assets have been compiled/saved; no C++ build, editor restart or project-file regeneration is required.

## Quest-request routing correction

Corrected WBP_Dialogue.OnKeyDown so E / dialogue state 1 / selected choice 0 executes HandleQuestRequest. W / selected choice 0 again wraps the selection to 3. The former completed-delivery branch is now unreachable from E. Live graph readback confirmed both routes, and Blueprint compilation with warnings as errors passed. The earlier runtime suite exercised the request helper directly and did not catch the input-routing mistake.

The production catalog currently contains only 0_Delivery_001. After it is completed, a bank request correctly reports no available requests until another eligible row is authored. Add another row using the steps above to test subsequent acceptance; completed IDs remain excluded.

## Repeatable commissions

The 200 repeatable commissions are grouped as 40 per star tier: 14 delivery, 13 combat and 13 collection in each tier (70/65/65 overall). Combat and collection require actual progress before Luna accepts turn-in. Higher tiers require more defeats or pickups; prototype enemy health also scales with required defeat count. Names, objectives, target types and completion dialogue vary by commission.

| Stars | Existing difficulty enum | Base draw chance | Gold range |
| --- | --- | --- | --- |
| 1 | Easy | 50% | 15?54 |
| 2 | Normal | 28% | 60?138 |
| 3 | Hard | 14% | 180?375 |
| 4 | Insane | 6% | 500?1085 |
| 5 | Elite | 2% | 1400?2960 |

These chances apply when all 200 repeatable quests are eligible. Each quest's selection weight is respectively 50, 28, 14, 6 or 2. Filtering active quests and shared item types redistributes the draw among remaining eligible quests. Within an eligible tier, equal-weight quests have equal odds. Eligible one-time quests take priority; the original delivery is unchanged and pays its original zero reward.

DA_QuestBank.RepeatableQuestIDs controls replay eligibility; QuestWeights maps exact quest ID strings to positive integer selection weights. Missing/nonpositive weights fall back to 1. Completion retains a bounded unique history entry and permits a repeatable quest to be selected again. An active instance of the same quest remains blocked. There is no cooldown or permanent exhaustion; an immediate repeat is possible. For a new repeatable quest, author its row and optional item rule as above, add its ID to RepeatableQuestIDs, and set its QuestWeights entry.

Gold is credited exactly once per active quest completion. Calling completion again without accepting another instance does not pay again. A new accepted replay earns a new reward. Player Gold is runtime state with no display or persistence added. Four variants of each commodity share an item-type reservation, so unrelated requests can be active together.

New assets: Content/Game/Quests/Repeatable/DA_RQ_1Star_001.uasset through DA_RQ_1Star_040.uasset, and corresponding 2Star, 3Star, 4Star and 5Star ranges (200 rule assets total). Modified for this extension: BP_QuestBank, BP_Player, DT_Quests, DA_QuestBank, and the reusable BP_QuestBankValidation test actor. Text files: Scripts/build_repeatable_quests.py, Docs/RepeatableQuestCatalog.json, and this document. No NPC or dialogue Blueprint edits are needed for catalog growth.

Manual replay test: complete the original delivery, request a commission from Luna, note its star rating and promised gold, and return to Luna for combat/collection or Rein for delivery. Inspect the live BP_Player.Gold value in the Blueprint debugger. Re-interact without a new acceptance and confirm no extra payment. Accept another commission, and verify completed repeatables remain available while active duplicates/shared commodities are excluded. Hold E and verify normal menu/close behavior.

### Final replay validation

A clean PIE run passed the original 3/30/300 catalog suites, Luna/Rein integration, exact 15-gold and 2960-gold payouts, repeat acceptance, duplicate-payment prevention, item-type conflicts, and 200 weighted accept/complete cycles. The sample yielded 107 one-star requests and 3 five-star requests. All 200 commissions remained eligible afterward. The validator now performs one sampling cycle per tick to stay within Unreal's script limit; earlier oversized test batches triggered that limit and were replaced. No loop/runtime errors occurred in the final run. The temporary actor was removed and the level was not saved. All changed Blueprints compiled with warnings as errors.

## Combat and collection objective extension

BP_QuestItemRule.ObjectiveType accepts Delivery, Combat or Collection. None preserves legacy delivery behavior. ObjectiveTargetType is the enemy or item type to match. DT_Quests.requiredAmount is enforced for Combat/Collection. The original 0_Delivery_001 quest remains untouched.

BP_Player.QuestProgress is a map keyed by exact quest ID strings. Acceptance resets progress to zero, relevant events increment it up to the required count, and successful turn-in clears it. Replayed quests require new progress; previous kills or pickups do not carry over. Shared item-type conflicts still apply to collection and delivery, while combat quests can share enemy types.

BP_QuestEnemy and BP_QuestPickup inherit the existing BP_TestInteractable interface/mesh support. Acceptance spawns prototype actors at player-relative offsets of +350 to +1000 world-X units and ?650 world-Y units. Each actor gets up to eight collision-safe placement attempts. Placement uses AdjustIfPossibleButDontSpawnIfColliding. If fewer than the required count can spawn, the acceptance rolls back, cleans up its spawned actors and reports insufficient space. Move into an open area before trying again. This prototype placement is not navigation-aware or a finished encounter design.

Press E near a matching enemy sphere to inflict one damage. Standard Apply Damage events also work when DamageCauser is BP_Player; future weapons may call TakeQuestDamage with their owning player explicitly. Only a lethal hit reports a combat defeat. A used/dead target cannot report another defeat. Prototype targets have no AI, attacks or combat animations. Press E near a matching pickup cube to collect one sample. Pickups count only for active matching collection quests, disappear on successful collection and cannot be counted twice. A pickup with no matching unfinished quest stays available.

Once the combat or collection objective count is met, speak to Luna to complete the quest and receive gold. Deliveries still turn in to their specified recipient, currently Rein. Unfinished requests cannot pay or move into completed state. Completion cleans up leftover prototype actors owned by that request and player. These are runtime actors; no level layout or existing assets are deleted.

New gameplay assets:

- Content/Game/Quests/Objectives/BP_QuestEnemy.uasset
- Content/Game/Quests/Objectives/BP_QuestPickup.uasset

Modified gameplay assets: BP_QuestBank, BP_QuestItemRule, BP_Player, DT_Quests and the 200 DA_RQ_* rule assets. The validation Blueprint is extended separately. NPC and dialogue graphs retain their existing bank routing.

To author another combat/collection quest:

1. Add its DT_Quests row using the existing instructions and set requiredAmount to a positive objective count.
2. Add/register a BP_QuestItemRule instance; set ObjectiveType and ObjectiveTargetType.
3. For Collection, set SharedItemTypes to the same item type to prevent conflicting reservations. Combat can leave SharedItemTypes empty.
4. Add the row ID to DA_QuestBank.RepeatableQuestIDs and its weight to QuestWeights if it should replay.
5. Save. Bank acceptance spawns matching prototype targets automatically. No Luna Blueprint edits or permanent actor placement is required.

For manually placed targets, drag BP_QuestEnemy or BP_QuestPickup into an open area in the level. Set ObjectiveTargetType to the quest rule's matching type. Set MaximumHealth on enemies. Manually placed actors are not owned by a spawned request and are not removed by that request's cleanup. Both classes configure their inherited CubeMesh to block the existing Interact trace at BeginPlay.

### Mixed-objective verification and files

The final PIE run passed delivery compatibility, the original 3/30/300 catalog suites, actual nonlethal/lethal target damage, actual pickup collection, premature turn-in rejection, correct rewards, wrong-type rejection, capped progress, replay reset and 200 mixed weighted replay cycles. It restored active/completed IDs, progress and gold. Spawn-collision warnings represent rejected positions handled by retries; no Blueprint runtime errors or runaway loops occurred in the final run. The temporary validator was removed without saving the level.

Text files for this extension: Scripts/add_quest_objectives.py, Scripts/create_quest_objective_actors.py, Scripts/spawn_quest_objectives.py, Scripts/mix_quest_catalog.py, Docs/RepeatableQuestCatalog.json and Docs/QuestBank.md. Scripts/build_repeatable_quests.py and superseded one-time setup scripts now guard against overwriting the installed mixed catalog. These are editor migration/audit tools, not runtime dependencies. Final spawn retry logic and test exports are retained in Saved/QuestBankAudit.

Editor tests:

1. Complete the original delivery. Request repeatable quests from Luna until you have a combat or collection request; unrelated active quests may coexist.
2. Note its objective type, required amount, target and reward in the dialogue. Targets/pickups should appear nearby in world +X, within approximately 1200 units.
3. Talk to Luna before completing a combat/collection objective. Expect a progress response and no reward/completed state.
4. For combat, press E near the spawned spheres. Nonlethal hits must not increment QuestProgress; each defeated target increments once. For collection, press E near the matching cubes; each collected pickup increments once.
5. Meet the required count, speak to Luna and verify Gold increments by the promised amount exactly once. Re-interact without accepting another request and verify no extra payment.
6. Replay a completed combat/collection request and verify fresh zero progress and new spawned objectives. Confirm collection and delivery quests sharing item types cannot overlap.
7. Exercise the usual dialogue choices, hold/release E, close and reopen the dialogue. Use the Blueprint debugger's BP_Player instance to inspect QuestProgress, Gold and ActiveQuestIDs.

All changed Blueprints compiled with warnings as errors and assets were saved through MCP. No C++ build, project regeneration or editor restart is required. No existing assets, gameplay systems or level layout were removed.

## Quest description cleanup

All 200 repeatable acceptance descriptions now contain a short conversational request, a blank line, and one compact star/reward line. Repeated quest titles, duplicate difficulty wording and editor/control instructions were removed from Luna's speech. Objective counts and the correct turn-in NPC remain explicit. The original delivery is unchanged. Only DT_Quests.description values were edited in gameplay assets; all other row fields were checked unchanged through MCP readback. No widget layout or gameplay Blueprint edits were needed.

Text files: Scripts/quest_description_text.py (shared wording formatter), Scripts/mix_quest_catalog.py (uses the formatter for future authoring), and Docs/QuestBank.md. DT_Quests was saved through Unreal MCP. No Blueprint compilation, restart or project-file regeneration is needed for this text-only asset change. In Play, request one delivery, combat and collection quest; check the short paragraph, star/reward line and wrapping within the dialogue panel.

## Turn-in routing: Luna for combat and collection

All 65 Combat and 65 Collection rows now set targetNPC to Luna. Their concise acceptance dialogue says to report/bring samples back to Luna, and objectiveText names Luna explicitly. All 70 repeatable Delivery rows and the original delivery remain unchanged, targeting Rein. This is catalog configuration; NPC and bank gameplay graphs continue to resolve the row's recipient, with no hard-coded routing added. Luna's existing CompletesQuestOnInteract setting was inspected and is enabled.

Modified files: Content/Game/Quests/Blueprints/DT_Quests.uasset, Content/Tests/QuestBank/BP_QuestBankValidation.uasset, Scripts/quest_description_text.py, Scripts/mix_quest_catalog.py, Docs/RepeatableQuestCatalog.json and Docs/QuestBank.md. No rule assets, NPC graphs, reward values, difficulty weights or objective counts changed. Future catalog generation preserves the same recipient choices. The catalog JSON now includes turnInNPC alongside objective target types.

Editor check: accept one combat quest and one gathering quest, meet their counts, then speak to Rein; neither should complete or pay. Return to Luna and verify completion and one reward payment. Accept a delivery and verify Luna cannot turn it in, while Rein can. An unfinished combat/gathering request should still show progress at Luna and pay nothing. No restart or project regeneration is required; the data table is saved and the validation Blueprint is compiled.

Routing validation passed in PIE: Luna's actual ResolveQuestDialogue completed both combat and collection objectives with the expected gold; Rein was rejected even when those objectives were ready. Delivery compatibility and 200 data-driven mixed replay cycles passed. The final run had zero validation failures and no Blueprint runtime/loop errors. The temporary actor was removed; the level was not saved.
