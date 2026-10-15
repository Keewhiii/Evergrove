# Woodland sprite props and closer camera

The subsequent [Breeze woodland revision](BreezeWoodland.md) further adjusts the camera to width 1200 and pitch -34, refines trees and flowers, and adds intermittent gusts and falling leaves.

October 15, 2026 revision: orthographic gameplay width reduced from 2400 to 1450 (approximately 1.66 times larger on screen). Camera retains its fixed direction and follow behavior.

Blender source: `ContentSource/PixelProps/AdventureRPG_PixelProps.blend`, scene `PixelProps_Studio`. Export/import scripts: `Scripts/build_pixel_props.py`, `Scripts/import_pixel_props.py`. Unreal assets live in `/Game/Environment/PixelProps`.

- Bush: three complete flat leaf sprites at separate heights, using the same leaf texture and green palette materials as the trees. All placed bushes have zero pitch/yaw/roll.
- Grass: two overlapping upright flat leafy tuft sprites. The older thin wheat-like grass and fern geometry is replaced, including runtime dressing.
- Rock: one flat mossy gray pixel sprite with broad facets; no textured solid stone geometry.
- Lantern: one upright flat dark-post sprite with a stepped base and warm glass. A selective emissive shader brightens the pale glass while preserving the dark post.

Three transparent textures were generated using the built-in ImageGen skill and copied into this source folder. Their original files remain in the Codex generated images directory. Sprite alpha is preserved; UVs crop transparent margins without modifying the PNGs. All textures use nearest sampling and no mipmaps. Materials are two-sided, masked, and unlit. No new collision or navigation blockers are introduced.

`Scripts/build_cozy_outing.py:scenery()` now uses the same assets for runtime bushes, grass, stepping stones and all five lanterns. Other guild dressing and quest behavior are preserved.

Validation: `Saved/PixelPropsAudit/migration.json` records the placed replacements and collision checks; `runtime.json` records the actual Play mode camera and runtime prop counts. `Game_Zoomed.png` is an editor screenshot of Play mode, including editor UI. The packaged game is rebuilt under `Saved/BaselinePackage/Windows`.
