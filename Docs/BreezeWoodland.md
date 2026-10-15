# Reference woodland and occasional wind

Current leaf motion: [Spatial wind leaves](SpatialWindLeaves.md) replaces the original descent with gust-driven sideways transport and independent 3D tumbling at varied depths.

The subsequent [woodland motion pass](WoodlandWindFX.md) adds gentle continuous tree sway, stronger sway with visible curved wind streaks, and leaf bursts when running through grass or bushes.

The new reference pass keeps the 2D layered construction. Five complete canopy sprites sit above a shortened flat trunk; broad lower tiers conceal most of the trunk, leaving the flared roots visible. Three-flower daisy clusters replace the earlier scattered cross shapes. White and yellow variants use flat pixel tiles in Blender. The gameplay camera remains orthographic at width 1200, with a shallower pitch of -34 degrees (previously -42). Its follow offset is 2224 cm along Y at height 1500 cm to keep the player centered. `Scripts/lower_woodland_camera.py` applies this camera refinement.

Source: `ContentSource/BreezeWoodland/AdventureRPG_BreezeWoodland.blend`, scene `BreezeWoodland_Studio`. Unreal assets: `/Game/Environment/BreezeWoodland`. Authoring: `Scripts/build_breeze_woodland.py`, `Scripts/import_breeze_woodland.py`. Runtime guild flowers use the same assets through `build_cozy_outing.py:scenery()`.

Wind occurs in gust windows of roughly twelve seconds, separated by roughly twenty seconds of calm. A shared time envelope synchronizes the canopy, bushes, grass, flowers and airborne leaves. Spatial phase and two sway frequencies keep the foliage from moving in lockstep; height weighting leaves the bases planted. Trunks and lantern posts stay fixed. `WindStrength` is an exposed scalar material parameter.

Falling leaves are 220 small flat stepped silhouettes authored in Blender. The single lightweight mesh covers the hub and trail. Independent per-leaf phases produce staggered falling and lateral flutter; gust-dependent mask thresholds release them gradually and hide them during calm periods. They loop without spawning actors every frame. The leaf field casts no shadows, has no collision, and does not affect navigation. This is an ambient gust effect, not a rain or season system.

The shader time envelope is `clamp((sin(2*pi*time/32)-0.35)/0.65, 0, 1)`. Leaf fall cycles are twelve seconds, with 5.1 metres of vertical travel and 6 metres of sideways travel. The leaf mesh bounds are expanded for shader motion and the actor is always loaded.

## Directional leaf refinement

`SM_DirectionalLeafField` uses leaves 50% larger than the initial pass. They travel sideways at 50 cm/s while descending, with a small flutter. `WindDirectionSign` controls the predominant direction: -1 is screen-left, +1 is screen-right for the fixed woodland camera. `HorizontalTravel` controls drift distance independently of `FallTravel`.

The current woodland uses `MI_BreezeLeaves_Left`. `MI_BreezeLeaves_Right` is also provided in `/Game/Environment/BreezeWoodland`. Future towns/routes can select the preset in the `Woodland_IntermittentLeaves` mesh component's material override, or create their own child instance with its own `WindDirectionSign`. The setting is per component/material instance, so changing one route need not change another. No future town or route selection logic is assumed.

`Scripts/apply_directional_leaves.py` imports the enlarged Blender export, configures the shader and presets, and updates the current field. `Scripts/validate_directional_leaves.py` checks both presets in Play mode. Evidence: `directional_leaves.json`, `directional_runtime.json` and `Directional_Left.png`/`Directional_Right.png` under the audit folder.

Validation records are under `Saved/BreezeWoodlandAudit`. `migration.json` records tree/flower replacements and collision checks. `runtime.json` records the real Play mode camera, leaf field and animated material connections. Calm, gust and subsequent calm screenshots include the editor interface. The Windows package is rebuilt under `Saved/BaselinePackage/Windows`.
