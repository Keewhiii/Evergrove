# Quest journal

Open with J during gameplay. W/S or Up/Down selects a quest, Tab switches active/completed views, Page Up/Page Down scrolls the description, and J or Escape closes. The journal uses UI-only input while open and restores game input on close. Opening is blocked while NPC dialogue is visible, and repeated open requests do not stack journal instances.

Assets:
- /Game/Game/UI/WBP_QuestJournal
- /Game/Game/UI/T_QuestJournal_Frame
- BP_Player.OpenQuestJournal and its J keyboard event

The widget reads BP_Player.ActiveQuestIDs and CompletedQuestIDs and resolves rows through the player's existing QuestBank. Quest names, descriptions, objective text, reward amounts and recipient names come from the catalog. Combat progress uses QuestProgress; collection uses InventoryItems, with surplus capped to the required amount for display. Readiness uses the existing bank check. Delivery quests show their recipient. The journal never accepts, completes or rewards quests. Progress refreshes on opening or changing selection/views. Completed history follows the bank's existing unique-ID history rather than counting every repeat completion. No save-game persistence is added.

The generated journal frame matches the dialogue artwork. The title, list, description, fixed reward row and keyboard hint are separate UMG text. Dark brown text provides contrast on parchment. Lists and details scroll within their panels. BuildJournal constructs the scrolling containers at runtime; edit its graph to change their layout. Designer canvas slots control the frame/title layout. Graph exports are in Saved/QuestJournalAudit.

Validation: BP_QuestJournalValidation in /Game/Tests/QuestJournal checks empty active/completed views, delivery recipient, catalog rewards, combat progress/readiness, inventory-based collection progress/readiness, surplus display, completed status, closing/reopening, duplicate-instance prevention and reward neutrality. All 14 checks passed in PIE, with FailureCount=0 and no Blueprint runtime errors. A runtime screenshot was inspected to verify text wrapping and panel placement. Physical J/W/S/Tab/Escape navigation still needs a manual check because the Windows input helper was unavailable. A temporary validation actor was removed without saving it into the level. The validator uses temporary PIE player data; stop Play after running it.

To verify manually: Play L_Prototype, press J before accepting a quest, close it, accept a quest from Luna, and reopen. Check W/S, Tab, scrolling, and J/Escape. Gather or defeat targets, reopen to check progress, turn in normally, and verify the completed view. Ensure movement and NPC interaction work after closing.
