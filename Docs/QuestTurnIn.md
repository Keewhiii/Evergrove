# Explicit quest turn-in

Luna's dialogue menu now includes **Turn in Quest Items** between area advice and Nothing right now. Use W/S to select and E to submit. The original request, guild, advice, and exit choices remain available. The new row is created once per widget instance at runtime in a matching button wrapper. All choices use Roboto Bold, size 15, left justification, left-aligned content, and identical button-slot padding (4 horizontal, 2 vertical). All row slots fill the menu width. The dynamic TextBlock uses the native SetFont method to update its Slate rendering. Scripts/style_dialogue_choices.py applies this focused styling migration.

Choice-bearing NPCs greet without automatically completing quests. Delivery recipient Rein retains automatic delivery completion. TurnInQuests reuses the bank's existing completion flow, target-NPC checks, dialogue, rewards, active/completed state, and objective cleanup.

Collection readiness reads BP_Player.InventoryItems, a string-to-integer map keyed by item type. BP_QuestPickup.CollectForPlayer calls RecordCollectedItems to add one item. Successful gathering turn-in subtracts only the required amount, preserving surplus. Event counters alone cannot satisfy collection readiness. There was no separate inventory implementation in the inspected project; this map is the shared quantity store for quest pickups. Future inventory grants/removals must update this same store. It does not introduce save-game persistence.

Combat readiness uses existing per-quest QuestProgress, updated by the enemy's lethal-damage path. Wrong target types, nonlethal damage, and completed/absent quests do not satisfy another objective. Repeated turn-ins cannot grant duplicate rewards.

## Changed assets

- Content/Game/Characters/Player/Blueprints/BP_Player.uasset
- Content/Game/Quests/Blueprints/BP_QuestBank.uasset
- Content/Game/Quests/Objectives/BP_QuestPickup.uasset
- Content/Game/Characters/NPCs/BP_Npc.uasset
- Content/Game/Characters/NPCs/WBP_Dialogue.uasset
- Content/Tests/QuestBank/BP_QuestBankValidation.uasset

All asset writes were performed through Unreal's MCP graph/editor APIs. No C++, configuration, or map changes are required. Blueprints are compiled and saved; restart and project-file regeneration are unnecessary.

Supporting text files changed: Scripts/quest_bank_mcp.py (MCP return-node compatibility), Scripts/explicit_quest_turnin.py, Scripts/quest_turnin_menu.py, Scripts/validate_quest_turnin.py, and this document. Generated graph sources and test evidence are under Saved/QuestBankAudit.

Editor validation passed with FailureCount=0 and ReplayDrawCount=200. Checks cover 3/30/300 quest fixtures, original delivery dialogue, lethal/nonlethal combat, real collection pickups, explicit widget turn-in, five menu rows with no duplicates, inventory-only gathering readiness, exact consumption, surplus retention, duplicate reward prevention, and replay/weighted selection. Evidence: Saved/QuestBankAudit/explicit_turnin_validation.json. Visual frame fit and physical keyboard navigation still need the manual checks below.

## Editor checks

1. Play L_Prototype, talk to Luna, press E to open her choices, and verify all five rows fit the dialogue frame. Check W/S wrapping and E selection, including Nothing right now.
2. Accept a gathering request. Select Turn in Quest Items before gathering enough: expect an incomplete progress reply, no reward, and no item consumption.
3. Gather the required type/quantity. Talking to Luna alone must not complete it. Select Turn in Quest Items: expect completion dialogue, the exact reward, and required items removed. Extra quantities remain.
4. Accept a combat request. Nonlethal hits must not qualify. Defeat the required targets, then select Turn in Quest Items at Luna to receive completion dialogue and reward.
5. Select turn-in again: no second reward. Request another quest and verify repeatable quests still work.
6. Complete a delivery at Rein and verify its existing dialogue/completion behavior.

Scripts/explicit_quest_turnin.py is a one-time editor migration, not a gameplay script. Scripts/quest_turnin_menu.py authors the menu graphs; Scripts/validate_quest_turnin.py updates the validation graphs. Do not rerun migration scripts as part of game startup.
