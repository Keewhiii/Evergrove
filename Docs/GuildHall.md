# Guild hall exterior, interior and walk-through doors

The temporary open NPC shelter has been replaced by a world-scaled guild landmark. Its exterior is about 19.7 metres wide with an 18 metre bell-tower finial. The original shelter remains hidden as a migration backup. The gameplay camera now uses a 31-degree angle and close town framing, with smooth character following on both interior floors. See [DayNight.md](DayNight.md).

Editable Blender sources:

- `ContentSource/GuildHall/AdventureRPG_GuildHall.blend`
- `ContentSource/GuildInterior/AdventureRPG_GuildInterior.blend` (`GuildInterior_Studio`)

The interior uses the user's two-floor reference layout: a dedicated central reception station, symmetrical staircases, and a shared upstairs gallery. Its 26 by 26 metre cutaway room contains communal tables and benches, sofas, a bordered guild rug, libraries, curtains, a clock, guild notices, a wall map, and warm lantern panes. This is just over twice the original 18 by 18 metre floor area. Furniture remains human-scale; its assemblies are spaced apart while the shell, stair treads, gallery and rug expand. Painted oak/plaster textures, bevels and flat layered foliage retain the cartoon art direction. Luna is the receptionist; Rein stands beside the station. Both retain their existing dialogue and quest fields. The request board is currently decorative; quest interaction is through the NPCs.

The front crossing, central aisle, both side aisles, reception rear passage and upstairs gallery have clear running routes. Tables, benches and sofas use simple solid footprint colliders to avoid catching the player under thin tabletop or seat edges. Eight tagged `GuildNPCSpawn` target points reserve future NPC locations away from the main running lanes; they do not spawn extra NPCs yet. Their coordinates are recorded in `ContentSource/GuildInterior/npc_spawn_points.json`. Room measurements and interaction coordinates are in `room_layout.json`.

The broad hall and upstairs gallery also draw inspiration from [Fairy Tail's guild building](https://fairytail.fandom.com/wiki/First_Fairy_Tail_Building). The supplied game screenshots guide the art style; this is an original guild layout and heraldry.

## Door behavior

`/Game/Game/World/BP_WalkThroughDoor` is a reusable linked doorway. Editable fields are Destination, DestinationYaw, TriggerWidth, TriggerDepth, LeftLeaf and RightLeaf. Door leaves are regular movable mesh actors with their origins at the hinges, so they are visible in both the editor and gameplay.

Approaching within 3 metres opens the exterior leaves outward to 85 degrees. Approaching alone does not transport the player. Walking into the doorway after the leaves open triggers a short fade and moves the existing player to the linked destination. Input is briefly held only during that transition, then restored. Walking away closes the leaves. Aperture checks and a cooldown prevent wall-side activation and immediate re-entry.

The interior exit has no leaf actors or door model. Walking into its front threshold returns outside. The interior remains in the same persistent world, so inventory, quests, party and save state are not reset by a map load. Interior geometry is staged at `(0,-6000,0)` centimetres, outside the woodland's visible area. The follow camera snaps across the transition and follows elevation on the stairs. Navigation bounds include both floors; the guild is a safe hub. Outdoor wind ribbons are hidden indoors.

## Ground detail

`/Game/Environment/CartoonGround/M_PaintedGrass` and `M_PaintedRoad` use world-space, limited-palette painted patches and sparse pixel accents. The visible pixel ground and irregular trail meshes use these materials. Existing grass interaction, tree sway and leaf effects remain intact.

## Authoring and validation

1. Run `build_guild_interior.py` in Blender, with the exterior source available. It invokes `polish_guild_interior_blender.py` and `expand_guild_layout_blender.py`, then exports editable geometry plus FBX and collision manifests.
2. Run `author_guild_doors.py`, then `import_guild_interior.py` through the Unreal MCP helper environment.
3. Run `detail_cartoon_ground.py` and `finish_guild_interior.py` for materials and navigation/safe-hub bounds.
4. Run `validate_guild_interior.py` in the editor environment. It uses real CharacterMovement to check approach/open/close behavior, entry, exit, both stairs, six sprint routes at 600 cm/s, wall-side rejection and the player's actual interaction trace across reception. Its temporary probe is removed in a finally block.

Generated oak and plaster assets are stored in `ContentSource/GuildInterior/T_Interior_Oak.png` and `T_Interior_Plaster.png`. They were created with the built-in image-generation tool; exact prompts are in `ContentSource/GuildInterior/ArtPrompts.json`. Mesh/material installation records, runtime results and native screenshots are in `Saved/GuildInteriorAudit`.

The old `BP_AutoDoor` prototype is superseded and has no placed instances. Future buildings can use `BP_WalkThroughDoor` with their own paired destinations and optional exterior leaves.
