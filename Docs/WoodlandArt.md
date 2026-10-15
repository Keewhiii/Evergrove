# Blender woodland art

## Current tree construction: stacked 2D elements

The latest user correction requires flat trunks and complete flat leaf sprites
stacked at separate heights. The authoritative Blender file is now
`ContentSource/LayeredWoodland/AdventureRPG_LayeredWoodland.blend`, scene
`StackedLeaf_Studio`; final mesh names are `SM_Stacked2D_Tree_*`. All 87 map trees
use these assets. The gameplay camera is orthographic. See `LayeredTrees.md`
for construction, authoring and validation. Earlier tree prototypes below are
superseded; the other woodland dressing remains.

## Earlier pixel-art revision (October 15, 2026)

The latest tree close-ups supersede the earlier canopy drawing. Current tree
crowns use large scalloped tiers, a rounded lime top with sparse swirl strokes,
deep teal hanging foliage, and a flowered variant. These painted textures were
made with built-in ImageGen from the user's two pictures; the blue symbol was
excluded. Source images and exact prompts are recorded in
`ContentSource/PixelWoodland/ScallopedFoliage_Prompts.md`. The new textures are
`T_ScallopedCrown.png` and `T_ScallopedFlower.png`; the Blender source and FBX
exports were updated. `Scripts/apply_scalloped_foliage.py` binds them in Unreal.
The saved map was reloaded successfully with the new materials.

The user's supplied image supersedes the earlier visual reference. The current
map uses painted, scalloped pixel leaf silhouettes and chunky broad-leaf grass,
with thick modeled trunks, flower variants, a simpler green floor and a flat-color
dirt trail. Tree crowns, low shrubs and tall grass are masked mesh cards designed
for the fixed RPG camera. Their painted shading stays legible through unlit
foliage materials; modeled trunks and ground receive the scene lighting.

Current Blender source: `ContentSource/PixelWoodland/AdventureRPG_PixelWoodland.blend`.
Current imported assets: `/Game/Environment/PixelWoodland`.
Preview: `Saved/PixelWoodlandAudit/PixelWoodland_Close.png` and
`PixelWoodland_Overview.png` (editor art previews).

There are 87 card-crown trees, 321 chunky grass cards, 50 low shrubs, 40 ferns
and 39 flower clusters. Previous grass is hidden. There are 765 tagged art actors
in total, including 215 hidden previous grass pieces. Existing rocks/logs/stumps
and the guild remain. Camera FOV is 48, with restrained depth of field. The
runtime cozy dressing uses ten matching shrubs, ten flowers and ten ferns.

The visible art passed collision/navigation checks with no issues. The 345 added
pixel actors survived a save/reload round trip; existing 420 art actors were
retained. PIE independently confirmed the player and updated runtime foliage.
No physical keyboard playtest or standalone launch is claimed.

Authoring: run `build_pixel_woodland.py`, `build_pixel_card_trees.py`, and
`build_pixel_grass_cards.py` inside Blender. The editor migration scripts are
`import_pixel_woodland.py`, `import_pixel_card_trees.py`, and
`import_pixel_grass_cards.py`. `build_cozy_outing.py` supplies matching runtime
shrubs. `preview_pixel_woodland.py` temporarily hides editor volume outlines for
captures, then restores them. Earlier geometric prototypes remain available in
the source scenes; the active final foliage assets are `SM_Pixel_CardTree_*_Front`,
`SM_Pixel_CardBush` and `SM_Pixel_CardGrass`.

## Earlier art pass (superseded)

The outdoor map `/Game/Maps/L_WoodlandBlockout` now uses an original woodland
kit authored in Blender, with Gamma Emerald's dense green foliage, pixel
textures, layered forest borders and sunlit clearings as the visual reference.
This is a stylized interpretation rather than a copy of its assets or layout.
Reference: https://undreamedpanic.itch.io/gamma-emerald-demo

## Source and imported assets

- Blender source: `ContentSource/Woodland/AdventureRPG_Woodland.blend`.
- The separate `Woodland_AssetStudio` scene contains the kit; the original
  starting Blender scene was preserved.
- Thirteen FBX exports and their metre-scale dimensions and triangle counts:
  `ContentSource/Woodland/FBX/` and `ContentSource/Woodland/manifest.json`.
- Unreal assets: `/Game/Environment/Woodland`.
- Three broadleaf trees, bush, fern, grass clump, two moss rocks, fallen log,
  stump, wildflowers, continuous ground skin and irregular trail skin.
- A shared lit, two-sided material uses `T_Woodland_Atlas_Crisp` with nearest
  filtering. The PNG source is `T_Woodland_PixelAtlas.png`.

The map has **420** tagged `WoodlandBlenderArt` actors, including **87 trees**.
They live under `Woodland/Blender Art` in the Outliner. Old blockout tree,
ground, trail, clearing and boundary render components are hidden; the existing
ground and obstacle collision remains authoritative. New art has no collision
and does not affect navigation. The trail centre and objective clearings remain
open. The pre-existing guild building and lantern/planter style remain.

`BP_CozyWoodland` also uses the Blender bush, fern, flower and rock meshes for
its outdoor dressing: **35 runtime components**. Its guild decorations remain.
The introductory quests were not reauthored.

The directional light is angled at pitch -43, yaw -35. An unbound post-process
volume provides manual exposure (physical camera exposure disabled, bias 0),
slightly increased saturation/contrast, and restrained bloom.

## Authoring and verification

`Scripts/build_blender_woodland.py` runs inside Blender and exports the kit.
`Scripts/import_blender_woodland.py --import` imports missing assets and sets
up the shared material. `--dress` requires an undressed woodland map and refuses
to duplicate an existing art pass. `--verify` checks art collision and navigation.
`Scripts/build_cozy_outing.py` now uses the imported models for outdoor dressing.
`Scripts/preview_blender_woodland.py` captures an editor view from the game-style
camera angle; it is an art preview, not a physical-input gameplay recording.

October 15, 2026 validation:

- All 13 FBX meshes imported at the expected centimetre scale.
- All 420 static art actors passed collision/navigation checks with zero issues.
- Saved all dirty packages through Unreal's native API, including external
  actors. Leaving the map and reloading it retained all 420 actors.
- Updated scenery Blueprint functions compiled successfully.
- PIE spawned the player at trail X 2650, Y 0 and Z 90.15; one cozy dressing
  actor had 147 mesh components, including the 35 imported-model components.
- The MCP StartPIE helper reports `PIE ended before warmup completed` even when
  the session remains active. The active session and runtime actors were checked
  independently, then PIE was stopped.

Evidence and pre-art component/transform snapshots are in
`Saved/WoodlandArtAudit/`. `Woodland_Editor.png` is the reviewed art preview.
The old `Woodland_Runtime.png` is also an editor-view capture and should not be
treated as a gameplay screenshot. The desktop helper was unavailable, so no
physical keyboard playtest or standalone launch is claimed by this pass.

Unreal's `save_assets` tool with an empty asset list calls
`EditorLoadingAndSavingUtils.save_dirty_packages(True, True)`. It saves the new
external actors without requiring a UI Save All action.

The updated Windows package completed BuildCookRun successfully (24.22 seconds,
exit code 0). Executable: `Saved/BaselinePackage/Windows/AdventureRPG.exe`.
