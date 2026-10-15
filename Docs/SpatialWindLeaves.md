# Leaves carried through 3D space

This replaces the earlier gravity-led leaf motion. A gust now carries ambient leaves predominantly sideways, at roughly 180–280 cm/s times gust strength plus a small base speed, while descent varies by leaf over 13–20 seconds. The transport integrates the same gust envelope used by the visible wind and trees; leaves accelerate as the gust builds and slow as it subsides. Small eddies add lateral depth movement and lift. The left/right route material presets remain supported.

The mesh contains 220 independently seeded leaves at heights from 0.9–5.8 m and across 22 m of scene depth. Foreground leaves are larger than distant leaves. Each leaf stores its own pivot offsets and flight data in three UV channels. The shader rotates every leaf around its own pivot on two axes, so it tumbles and turns edge-on rather than remaining a fixed camera-facing card. The elements are still flat 2D artwork arranged and animated in 3D; masked materials use normal scene depth and occlusion.

Running bursts also use pivot data and 3D tumbling. During a gust their outward spring is carried up to 230 cm in the wind direction before the short burst expires.

Blender source: `ContentSource/WoodlandWindFX/AdventureRPG_SpatialLeaves.blend`, scene `SpatialLeaves_Studio`. Mesh assets: `/Game/Environment/WoodlandWindFX/SM_SpatialWindLeaves` and `SM_SpatialRunLeafBurst`. Scripts: `build_spatial_wind_leaves.py`, `apply_spatial_wind_leaves.py`. The existing `M_BreezeFallingLeaves` material and left/right instances are updated so the current route uses the new motion automatically. The current route remains leftward.

The ambient field wraps outside the main scene to keep route coverage during strong sideways transport. Individual descent cycles remain staggered. All leaf meshes have no collision, and the ambient field casts no shadows. Camera zoom and angle are unchanged.

Audit records and Play mode frame captures are under `Saved/WoodlandWindFXAudit`.

Validation: imported mesh bounds span about 21.7 m in depth and 5.1 m vertically. `validate_spatial_wind_leaves.py` checks those bounds, collision/navigation settings, both route direction presets, and captures successive gust frames. `validate_woodland_wind_fx.py` also verifies the updated running bursts still spawn only near vegetation while running, then clean up after stopping.
