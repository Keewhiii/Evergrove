from pathlib import Path
import math,random
verts=[];faces=[]
def poly(points,mat):
 start=len(verts);verts.extend(points);faces.append((mat,list(range(start+1,len(verts)+1))))
for k,(cx,cy,r) in enumerate([(-31,-15,23),(23,19,28),(34,-32,16)]):
 pts=[(cx+math.cos(i*math.tau/22)*r,cy+math.sin(i*math.tau/22)*r,1+.5*math.sin(i*2.3)) for i in range(1,22)]
 center=(cx,cy,1.7)
 for a,b in zip(pts,pts[1:]):poly([center,a,b],'PadLight' if k==1 else 'PadDark')
 # A V notch gives each floating leaf a readable lily-pad silhouette.
 if k==1:
  for i in range(7):
   a=i*math.tau/7
   poly([(cx,cy,3),(cx+math.cos(a-.4)*4,cy+math.sin(a-.4)*4,5),(cx+math.cos(a)*10,cy+math.sin(a)*10,4),(cx+math.cos(a+.4)*4,cy+math.sin(a+.4)*4,5)],'Flower')
  poly([(cx+math.cos(i*math.tau/9)*3,cy+math.sin(i*math.tau/9)*3,5.2) for i in range(9)],'Center')
lines=['o SM_ForestLilyPatch']+[f'v {x} {-y} {z}' for x,y,z in verts]
for mat,f in faces:lines+=['usemtl '+mat,'f '+' '.join(map(str,f))]
p=Path('ContentSource/ForestFeatures/SM_ForestLilyPatch.obj');p.write_text('\n'.join(lines))
