# Layered 2D tree assets

Current reference refinement: [Breeze woodland](BreezeWoodland.md) uses fuller canopies, shorter visible trunks, daisy clusters, a closer camera and occasional wind with falling leaves. The construction details below describe the preceding tree revision.

The intended art direction is **2D textured elements arranged in 3D space**.
Both trunks and foliage are flat sprites. The final canopy uses five complete
leaf-tier sprites at separate heights; it is not one full-tree billboard.

## Current assets

- Blender: `ContentSource/LayeredWoodland/AdventureRPG_LayeredWoodland.blend`.
- Active source scene: `StackedLeaf_Studio`.
- Final exports: `ContentSource/LayeredWoodland/FBX/SM_Stacked2D_Tree_A.fbx`,
  `SM_Stacked2D_Tree_B.fbx`, and `SM_Stacked2D_Tree_C.fbx`.
- Unreal: `/Game/Environment/LayeredWoodland/SM_Stacked2D_Tree_*`.
- Clean asset preview: `Saved/LayeredWoodlandAudit/LayeredTrees_Front.png`.

Each tree has one camera-facing trunk plane and five complete, masked leaf
planes. Leaf tiers sit at Z 2.4, 2.85, 3.3, 3.75 and 4.2 metres, angled 20
degrees from the ground. Their different sizes and heights, occlusion, and
shadows create the volume. The lowest foliage is dark teal and the upper tier
is lime green. The flowered variant adds only flat pixel-petal quads.

Plain trees have 12 triangles. The flowered tree has 62, including the flat
flowers. There are no polygon cylinders, extruded trunks, or solid canopy
volumes in these final mesh assets. The source objects are separately named
`A_FlatTrunk`, `A_LeafTier_1` through `A_LeafTier_5`, and equivalents for B/C,
parented to `Stacked2D_Tree_*` groups for easy editing.

All 87 map tree instances use the final assets and have zero pitch, yaw and
roll. Their original positions and uniform size variation are preserved.
Existing hidden blockout collision remains authoritative; decorative meshes
have no collision and do not affect navigation.

## Camera

`Woodland_FollowCamera` uses orthographic projection with OrthoWidth 1450 (reduced from 2400 in the subsequent [sprite prop revision](PixelProps.md)).
This keeps parallel sprite elements consistent across the gameplay view.
Free perspective inspection in the editor can still foreshorten flat planes;
Play mode uses the orthographic camera. The existing camera-follow behavior
and map bounds are unchanged.

## Authoring and validation

Run `Scripts/build_stacked_leaf_trees.py` inside Blender, then
`Scripts/import_stacked_leaf_trees.py` through the local Unreal MCP connection.
The import script builds masked palette shaders for each leaf tier and updates
the placed instances. `Scripts/render_layered_tree_preview.py` renders the
clean orthographic Blender preview. `Scripts/preview_layered_trees.py` checks
the actual PIE camera and saves a full-editor gameplay capture.

Source textures are `T_FlatTrunk.png`, `T_LeafTier.png`, and the flower palette
`T_LayeredPalette.png`. Built-in ImageGen produced the trunk and single leaf-tier
art from the user's references. Their prompts are in `ArtPrompts.md` beside the
Blender file. Images retain their alpha; trunk bounds are selected by UVs and
material masking, without modifying the PNG.

Validation on October 15, 2026: imported triangle counts match the source;
87 trees passed collision/navigation checks; all 87 survived map reload with
no tilted actors. Actual PIE independently confirmed orthographic projection
and OrthoWidth 2400 at the tree revision. The subsequent prop revision verifies width 1450. The Blender source and gameplay were visually inspected.
Evidence: `Saved/LayeredWoodlandAudit/stacked_validation.json`,
`runtime_camera.json`, and `LayeredTrees_Front.png`. Earlier prototypes remain
available in separate source scenes and assets.

The updated Windows package completed BuildCookRun successfully in 35.45 seconds
(exit code 0). Executable: `Saved/BaselinePackage/Windows/AdventureRPG.exe`.
The packaged executable was not separately launched during this pass.
