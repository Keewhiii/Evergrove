# Wind issue resolved

Resolved on 2026-10-15 at the user's request. Visible wind is anchored in world
space instead of following the player/camera. Its material animates the ribbons
across the woods. Guild interior hiding is preserved.

Regression: `Scripts/validate_world_anchored_wind.py` verifies a fixed wind
position while the player and camera move, plus interior hiding and restoration.
