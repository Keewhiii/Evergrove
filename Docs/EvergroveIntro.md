# Evergrove intro

The packaged game starts in `/Game/Maps/L_EvergroveIntro`. New Game enters the woodland map; the editor still opens the woods directly.

The title uses original woodland artwork and an ornamented Evergrove wordmark. Menu entries are floating Cinzel serif text with cream/gold selection colors and a small diamond ornament. The background slowly pans and breathes while fireflies drift across it. Options can disable that motion.

Mouse hit boxes cover each text entry. Up/Down or W/S select, Left/Right or A/D adjust settings, Enter/Space confirm, and Escape returns to the title.

The intro explicitly enables PlayerController click and hover events. Options support mouse selection and clickable adjustment arrows, alongside keyboard arrow navigation. The title, rural starting map, and legacy woodland maps are explicitly listed in packaging settings; name-based level travel alone does not create a cook dependency.

Load Game is enabled only when a readable version-1 rural or legacy woodland save exists. Its subtitle shows the saved day and clock time when available. The GameInstance carries a pending load across the level transition; the world restores the player and full-precision clock through the existing LoadProgress path. Failed loads return to the title with an explanation. Starting a new game leaves the old save on disk until the player explicitly saves again.

Options include display mode, scalability preset, resolution scale (50–100%), frame limit (30/60/120/unlimited), VSync, master volume, brightness, and menu background motion. Apply commits engine display settings and writes preferences to `Evergrove_Options.sav`; Back discards pending changes. Restore Defaults selects recommended settings and still requires Apply. The master volume uses a SoundMix override of the engine Master sound class, including child classes.

## Assets and attribution

Original image source files and their prompts: [ArtPrompts.md](../ContentSource/EvergroveIntro/ArtPrompts.md).

Cinzel by Natanael Gama is distributed under the SIL Open Font License. [Font source](https://github.com/google/fonts/tree/main/ofl/cinzel), [included license](../ContentSource/EvergroveIntro/Fonts/OFL-Cinzel.txt).

## Validation

`Scripts/validate_intro.py` uses a temporary test actor and isolated clock/preferences save slots. It checks the no-save state, saved time summary, new-game confirmation, options application and fresh-session persistence, restored Day 7 evening clock, and a fresh Day 1 new game. Screenshots and runtime observations are retained in `Saved/EvergroveIntroAudit`. The temporary actor is removed before the map is saved or packaged.

`Scripts/validate_packaged_intro.ps1` checks the packaged manifest for both maps, launches the archived executable with an isolated user directory, and verifies actual travel from the intro into the woods without runtime errors. This catches maps that work in the editor but were omitted from the packaged build.

Authoring scripts use Unreal APIs rather than binary asset editing. `create_intro_level_unreal.py` creates a clean menu world; `import_intro_font_unreal.py` imports the font; `author_intro_core.py`, `author_intro_behavior.py`, and `author_intro_art.py` create runtime assets; `author_intro_bridge.py` connects gameplay; `configure_intro_map.py` sets the startup map. `author_intro_inputs.py` creates native keyboard event bindings because the DSL event shorthand does not support those nodes.

New Game now plays the dream and forest awakening described in [OpeningSequence.md](OpeningSequence.md), then hands over control in the new [rural village map](RuralVillage.md). Load Game resumes its saved map without replaying the opening.
