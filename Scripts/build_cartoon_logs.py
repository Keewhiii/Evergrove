"""Rounded, tapered bark trunk with irregular end-grain rings and snapped branches."""
from pathlib import Path
import math
exec(Path('Scripts/build_forest_feature_assets.py').read_text().split('manifest=[]')[0])
m=Mesh();n=16

def radius(i):return 1+.045*math.sin(i*2.7)+.025*math.cos(i*4.1)
xs=[-148,-141,-119,-65,0,70,123,139,145];rs=[.79,.96,1.02,1.04,1,.98,.94,.88,.74]
rings=[]
for x,r in zip(xs,rs):
 cy=3*math.sin(x/80);cz=53+3*math.cos(x/100)
 rings.append([(x+2*math.sin(i*3.3) if abs(x)>135 else x,cy+math.cos(i*math.tau/n)*48*r*radius(i),cz+math.sin(i*math.tau/n)*46*r*radius(i)) for i in range(n)])
for k in range(len(xs)-1):
 for i in range(n):
  j=(i+1)%n;m.poly([rings[k][i],rings[k+1][i],rings[k+1][j],rings[k][j]],'Timber' if i%4 else 'Plank')
# Narrow darker grooves follow the bark, never turning the entire log into a striped barrel.
for i in [1,4,7,10,13]:
 angle=(i+.22)*math.tau/n
 pts=[]
 for k,x in enumerate(xs[1:-1]):
  r=rs[k+1]*radius(i)*1.015;a=angle+.025*math.sin(x/50+i)
  pts.append([(x,3*math.sin(x/80)+math.cos(a+d)*48*r,53+3*math.cos(x/100)+math.sin(a+d)*46*r) for d in [-.012,.012]])
 for a,b in zip(pts,pts[1:]):m.poly([a[0],b[0],b[1],a[1]],'Timber')
for end,side in [(0,-1),(-1,1)]:
 x=xs[end]+side*.8;cy=3*math.sin(x/80);cz=53+3*math.cos(x/100);r=rs[end]
 for lo,hi,mat in [(0,.18,'PlankLight'),(.18,.22,'Plank'),(.22,.40,'PlankLight'),(.40,.435,'Plank'),(.435,.63,'PlankLight'),(.63,.665,'Plank'),(.665,.87,'PlankLight'),(.87,1,'Timber')]:
  for i in range(n):
   def p(j,t):
    a=j*math.tau/n;rr=t*r*radius(j)+.018*math.sin(j*2+t*7)
    return (x,cy+math.cos(a)*48*rr,cz+math.sin(a)*46*rr)
   m.poly([p(i,lo),p(i,hi),p(i+1,hi),p(i+1,lo)],mat)
# Broken branch stubs rise obliquely from the trunk, with pale snapped ends.
for bx,by,bz,dx,dy,dz in [(-72,-20,85,-15,-22,29),(70,20,88,18,23,26)]:
 rings=[]
 for t,rr in [(0,15),(.65,11),(1,8)]:
  rings.append([(bx+dx*t+rr*math.cos(i*math.tau/9),by+dy*t+rr*math.sin(i*math.tau/9),bz+dz*t+2*math.sin(i*2.8) if t==1 else bz+dz*t) for i in range(9)])
 for a,b in zip(rings,rings[1:]):
  for i in range(9):j=(i+1)%9;m.poly([a[i],b[i],b[j],a[j]],'Timber' if i%3 else 'Plank')
 m.poly(rings[-1],'PlankLight')
print(m.save('SM_ForestCartoonLog'))
