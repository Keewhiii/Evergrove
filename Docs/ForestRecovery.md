# Forest recovery ? 2026-10-16

The 02:31 recovery run deleted and recreated L_EvergroveForest, then failed before forest placement completed. The cause was forest_water_surface.py assigning a StaticMesh to the shared global name `mesh`, replacing the placement helper function.

Recovery preserved maps, forest/village external actors and objects, ForestFeatures assets, scripts, configuration, and forest layout in Saved/ForestRecoveryBackup/20261016_023935. The water script now uses `water_mesh_asset`. The forest builder no longer deletes the map before rebuilding. A forest-only recovery script rebuilt the existing map in the owning editor, without modifying village geometry.

The recovered forest contains 804 trees, grassy routes, a river and bridge, a lake, two ponds, Rein, and a village exit.

Validation: the full grassy route was walked successfully. Bidirectional forest/village travel, exact fractional clock continuity, and gold preservation pass (the test now waits for its setup tick before travelling). Water contact checks pass for idle/moving/stopped states. The lake is calm at rest and the bridge channel is narrowed. Screenshots and contact evidence are in Saved/WaterAdjustmentAudit.
