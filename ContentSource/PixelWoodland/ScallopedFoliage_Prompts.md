# Reference-matched scalloped foliage

Created with the **built-in ImageGen tool**, October 15, 2026. The two user
reference pictures are preserved in `References/`. The blue symbol in the second
picture was explicitly excluded. Outputs retain their generated transparent alpha.

Final textures: `T_ScallopedCrown.png` and `T_ScallopedFlower.png`.
Blender source: `AdventureRPG_PixelWoodland.blend`.
Unreal textures: `/Game/Environment/PixelWoodland/T_ScallopedCrown` and
`/Game/Environment/PixelWoodland/T_ScallopedFlower`.

## Crown generation prompt

Use case: stylized-concept. Asset type: a single game-ready transparent pixel-art tree FOLIAGE CROWN sprite to texture a mesh in a fixed-camera HD-2D RPG. The attached images are STYLE AND SHAPE REFERENCES. Closely match the TREE in image 1, ignoring the background and neighboring trees, and ignore the blue symbol entirely in image 2. Produce ONE isolated complete foliage crown with NO trunk, NO ground, NO background, NO cast shadow, no text, no symbols. The crown has 4 to 5 broad overlapping scalloped leaf tiers, an almost circular lime-green top cap with only 3 or 4 big simple curved swirl highlight strokes, mid layers made of big drooping lobed leaves, and a deep teal-green hanging bottom tier. Rounded tall canopy silhouette, full and lush, slightly wider in the middle, like the tree reference. Do NOT fill it with lots of tiny oval individual leaves, rings, pebble shapes, veins, or texture noise. Flat color clusters, restrained palette, large legible shapes, crisp pixel-stepped contours. Match reference exactly in visual language: bright yellow-green top, medium leafy-green middle, dark turquoise forest-green bottom, understated darker tier outlines. Viewed from the same elevated top-down RPG camera as references, front-facing sprite, NOT an isometric cube, NOT a realistic rendered tree. Center the single entire crown upright in a portrait canvas with a small transparent margin all around. Intentionally low-resolution pixel art appearance equivalent to a 128x160 sprite enlarged with nearest-neighbor sampling. This is original art guided by the references, no watermark.

## Flower variant edit prompt

Use case: precise-object-edit. Image 1 is the EDIT TARGET: preserve this exact pixel-art foliage crown, silhouette, palette, lighting, all the broad scalloped tier shapes, and transparent background. Image 2 is ONLY a style reference for the little colored flowers growing on the tree. Ignore and exclude the blue symbol in the lower right of image 2. Make one flowered variant of image 1 by adding a sparse climbing trail of 7 small flowers among its lower and middle foliage: a few blue flowers with yellow centers, one or two magenta/pink flowers with yellow centers, and a few small cream-white flowers. Match the same chunky pixel scale of the crown, each flower about 6-9% of the crown width, clearly separated, asymmetrically arranged mostly down the left edge and a few on the right. Keep the big lime top cap clear so its swirl highlights stay visible. Preserve the original crown, do not redraw its leaf shapes or introduce little oval leaves. No trunk, ground, background, shadow, text, symbol, badge, logo or watermark. Real transparent alpha background.

## Integration

The existing Blender foliage-card materials now reference these workspace PNGs.
The tree and shrub FBX sources were exported again with the new texture references.
`Scripts/build_pixel_card_trees.py` prefers these painted inputs when present.
`Scripts/apply_scalloped_foliage.py` imports the textures and binds them to the
existing masked foliage materials, with nearest filtering and no mipmaps.
The material change updates all 87 map trees and matching shrubs, including
the runtime cozy woodland shrubs. The model placements and collision stay intact.

Verification: both PNGs retain transparent alpha; the Blender models and Unreal
preview were visually inspected, and the saved map was reloaded. Windows
BuildCookRun succeeded in 27.89 seconds (exit code 0). Standalone launch was not
separately tested.
