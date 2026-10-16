# Evergrove outskirts village

New games awaken in the separate `/Game/Maps/L_EvergroveForest` level. Its western gate leads to a path outside `/Game/Maps/L_EvergroveStart`, containing six homes, four small crop plots, a barn, a well, and a modest timber guild hall with a fieldstone base. The original grand guild remains in `L_WoodlandBlockout` for a future trading settlement and legacy saves.

Buildings and farms align to the X/Y axes, like the previous guild hall. Their centers have different offsets and gaps rather than mirrored rows. Town footpaths use right-angle turns around yards; the separate forest uses grassy passages through dense trees. Pokémon town layouts are a placement reference, with no Pokémon art used: https://pokemonletsgo.pokemon.com/en-us/kanto-region/

The spacing pass increases distances between village locations by 35% while retaining each structure's size. Connecting paths are 260 cm wide and yard approaches 190 cm wide. Bounds, camera range, trees, trunk collision, door return positions, and local lights follow the expanded layout. The ground's top stays at Z=0 so the paths remain visible.

Door leaves, wall colliders, entrances, return destinations, and window lights share each building's orientation. All eight structures have separate furnished interiors. Interior lighting stays constant; exterior window emission and local point lights fade with the shared world clock. The new map omits prototype combat display rows while retaining the combat system. Wind remains world anchored.

Source geometry and palette: `ContentSource/RuralVillage`. Layout metadata: `layout.json`. Authoring: `build_rural_assets.py`, `author_rural_map_unreal.py`, `author_rural_runtime.py`, then the routing, lighting, and environment polish scripts. `straighten_rural_layout.py` records the axis-aligned layout revision in both the editor map and source builder. Avoid regenerating a loaded map from a second editor process.

The final native map builder includes the axis alignment, expanded spacing, floors, and forest backdrop. `trigger_rural_rebuild.py` schedules it in the owning editor process after PIE ends, avoiding both external file locks and stale registry entries for World Partition actors. `verify_rural_persistence.py` reloads the map and checks all structure/farm transforms against the layout metadata. Earlier placement migration scripts are retained as history; rebuilding the final builder does not require repeating those migrations.

## Larger interiors and forest introduction

Homes now have 2200×1800 or 2500×1900 cm interiors (about 8–10 times the previous floor area), with a sleeping alcove, kitchen cabinets and wash basin, bookcases, dining table and chairs, hearth, storage chests, linens, curtains, skirting and wall posts. The guild and barn are larger too. Each interior is at least 12,000 cm from its neighbor, with a dark backdrop under the room to prevent neighboring houses or the sky void from showing at the edges. Furniture remains aligned to the axes with open walking lanes. Pokémon house layouts are a reference for the readable living, dining, kitchen and sleeping areas: https://bulbapedia.bulbagarden.net/wiki/Player%27s_house

`rural_interior_details.py` authors the furnishings. Explicit `use_default_collision=False` preserves the intended decorative/no-collision settings after reload; walls, floors and larger furniture keep their collision. The separate forest has unpaved grassy passages, side branches, wooden markers and dense thickets. Rein finds the player in its eastern clearing. See EvergroveForest.md for the final forest layout. `schedule_hunter_placement.py` applies the final hunter position, collision settings, backdrop and clearing visibility polish in the owning editor.

`validate_expanded_rooms_and_forest.py` walks the forest route with movement input, visits multiple homes, the barn and guild, checks room isolation, and compares actual indoor sun intensity/color across day and night. Evidence: `Saved/ExpandedRoomsAudit`.

Validation evidence: `Saved/RuralVillageAudit`; executable: `Saved/BaselinePackage/Windows/AdventureRPG.exe`. Cook explicitly includes the title, separate forest, rural town, and original woodland maps.

`preview_rural_village.py` walks the forest route using CharacterMovement input, checks the guild portals, and verifies exterior window intensity is 350 at night and 0 by day while interior daylight remains stable. `validate_rural_clock_runtime.py` checks exact disk restoration and a fresh session in the rural map, preserving the separate legacy woodland save fixture. Observed time: day 7, 1163.4567890123 minutes, with the clock continuing afterward.
