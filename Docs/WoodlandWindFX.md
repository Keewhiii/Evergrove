# Woodland motion and running leaf bursts

The subsequent [spatial leaf refinement](SpatialWindLeaves.md) adds much stronger gust-driven sideways transport, independent two-axis tumbling, varied depths and wind carry for running bursts.

Trees and layered bushes now always sway slightly. Their existing spatially varied sway is multiplied by `AmbientSway + 1.5 * gust`, with `AmbientSway` defaulting to 0.12. The same 32-second gust envelope drives the existing falling leaves and new visible wind ribbons, so the canopy moves more strongly during visible wind.

Six thin translucent wind trails sweep sideways around the player's view during gusts and fade during calm periods. Their shapes continuously deform: rolling curls rotate, a smooth moving bell shifts the curl along each trail, and slow lateral/vertical waves make them bend and unfurl. Each ribbon has 192 segments for smooth curves. `CurlStrength` controls this deformation. The local field follows the player, preventing empty stretches of route from missing the effect. The current direction is leftward; `M_VisibleWind.WindDirectionSign` can be set to +1 for a future rightward route. The mesh is movable, always loaded, collision-free, and casts no shadows.

Running through grass or a bush kicks out eight flat green leaves. Each burst has its own start time in custom primitive data: leaves spring up and outward, arc down, and disappear after 1.25 seconds. Bursts have no collision. Walking retains the existing grass bend/shake but does not release leaves. Running must exceed 330 cm/s with movement energy above 0.55; vegetation must be within 95 cm. The effect checks at most every 0.08 seconds and releases at most one burst every 0.22 seconds. It uses cached vegetation centers rather than adding collision to decorative grass.

`BP_WoodlandWorld.GrassLeafCenters` contains the placed visible grass and bush centers plus runtime guild vegetation. Future route dressing can supply its own centers. `GrassLeafBurstCount` provides a diagnostic counter. No leaf effects spawn while stationary or away from vegetation; existing bursts finish after the player leaves.

Blender source: `ContentSource/WoodlandWindFX/AdventureRPG_WoodlandWindFX.blend`, scene `WoodlandWindFX_Studio`. Both the eight-leaf burst and curved streak geometry are native flat Blender meshes. Unreal assets: `/Game/Environment/WoodlandWindFX`, plus `/Game/Game/World/BP_RunLeafBurst`.

Authoring: `build_woodland_wind_fx.py`, `author_woodland_wind_fx.py`, and the shared `woodland_fx_graph.py` helper. Validation: `validate_woodland_wind_fx.py`. The Play mode check moves the real player through grass, verifies zero idle/walking bursts, active running bursts, and complete cleanup after stopping. Temporary test actors are removed before saving. Audit records and full-editor captures are in `Saved/WoodlandWindFXAudit`.

Fluid curve refinement: `apply_fluid_wind.py` and `preview_fluid_wind.py`. `SM_FluidWindRibbonLocal` has 2304 triangles across six ribbons; its shader adds moving 115 cm rolling curls, 70 cm lateral waves and small vertical drift to the sweep motion. `FluidWind_1.png` through `FluidWind_4.png` capture different times during a gust, showing the changing shape rather than only rigid translation.
