# Broadleaf tall grass

The subsequent [woodland motion pass](WoodlandWindFX.md) adds leaves that spring out when running through grass or bushes, alongside the bend/shake behavior described below.

Replaces the narrow pointed grass tufts with dense, overlapping broad pixel leaves inspired by the earlier woodland references. The shader remaps the artwork into the trees' forest-green shadows and yellow-green highlights: RGB (9,58,40) to (117,172,47). The painted stepped silhouettes and broad flat shading remain visible. Three flat sprite layers make each tile; adjacent tiles overlap into patches. Each source tile is 0.88 m wide, about 0.53 m high, and six triangles. The main patches use fewer tiles at 1.6 scale, keeping individual leaf shapes large and readable. The camera remains at 34 degrees and orthographic width 1200.

Blender source: `ContentSource/BroadleafGrass/AdventureRPG_BroadleafGrass.blend`, scene `BroadleafGrass_Studio`. It includes separately editable layers and a linked repeated-patch preview. Unreal assets: `/Game/Environment/BroadleafGrass`.

`build_broadleaf_grass.py` authors and exports the mesh. `import_broadleaf_grass.py` installs the texture/material and updates placed tiles. The material duplicates the previous grass shader to retain occasional gusts and rooted sway. It uses unlit masked sprites, nearest texture sampling, and no mipmaps. Decorative meshes have no collision and do not affect navigation. Existing hidden grass stays hidden.

`finish_broadleaf_grass.py` updates the two affected runtime dressing graphs and verifies the ten runtime tiles in Play mode. `build_cozy_outing.py` also references the new assets for subsequent full authoring runs. Audit records and the full-editor Play mode screenshot are in `Saved/BroadleafGrassAudit`.

The transparent bitmap was generated using built-in ImageGen and copied unchanged to `ContentSource/BroadleafGrass/T_BroadleafGrass.png`. UVs crop transparent margins. Its original is `C:/Users/Ktcn2/.codex/generated_images/01a13ee3-102c-7772-924d-563a1b736da5/exec-ccb00dd3-090d-4807-b6aa-e657d44146fd.png`. The exact prompt is stored alongside the texture.

## Player interaction

`MPC_GrassInteraction.GrassInteractor` carries the player's position and smoothed movement energy. `BP_WoodlandWorld.UpdateGrassInteraction` updates it every frame through the existing world tick. Only nearby grass responds: a 105 cm radius with quadratic falloff, height-weighted outward bending, and a rapid shake. Running produces a stronger response than walking; movement energy smoothly decays after stopping. Grass outside the radius retains only the separate occasional ambient wind. The artwork and physical interaction are independent.

`add_grass_interaction.py` builds the palette and interaction graph. `space_broadleaf_grass.py` reduces dense rows to 81 larger overlapping patch/border clumps, hiding 240 redundant small clumps while retaining their editable actors. `validate_grass_interaction.py` uses a temporary movement driver to walk and run the real player through the grass, then verifies settling. The temporary actor is removed before saving and packaging. Readbacks are in `player_interaction_runtime.json`; observed energy was about 0.33 walking, 0.67 running, and 0.0001 after settling. Screenshots are `Grass_RunInteraction.png` and `Grass_TreePalette.png`.
