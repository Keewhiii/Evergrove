from forest_terrain_height import terrain_height
from pathlib import Path
xs=list(range(-800,14201,200));ys=list(range(-7700,6301,200));lines=['o SM_ForestRollingTerrain','usemtl Grass'];n=len(xs)
for y in ys:
 for x in xs:lines.append(f'v {x} {-y} {terrain_height(x,y):.5f}')
for y in ys:
 for x in xs:lines.append(f'vt {x/400} {y/400}')
for j in range(len(ys)-1):
 for i in range(n-1):
  a=j*n+i+1;b=a+1;c=a+n;d=c+1
  # Unreal OBJ flips Y; reverse winding to keep the terrain facing upward.
  lines.extend([f'f {a}/{a} {c}/{c} {b}/{b}',f'f {b}/{b} {c}/{c} {d}/{d}'])
p=Path('ContentSource/ForestAtmosphere/SM_ForestRollingTerrain.obj');p.write_text('\n'.join(lines));print('ROLLING_TERRAIN_SOURCE',len(xs)*len(ys))
