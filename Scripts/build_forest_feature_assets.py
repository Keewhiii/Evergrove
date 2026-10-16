"""Original rounded props and organic lake/pond/river surfaces, in centimetres."""
from pathlib import Path
import math,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'ContentSource/ForestFeatures';OUT.mkdir(exist_ok=True)
class Mesh:
 def __init__(self):self.v=[];self.faces=[]
 def poly(self,pts,mat):
  start=len(self.v);self.v+=pts;self.faces.append((mat,list(range(start+1,len(self.v)+1))))
 def save(self,name):
  lines=['mtllib ForestFeatures.mtl','o '+name]+[f'v {x:.4f} {-y:.4f} {z:.4f}' for x,y,z in self.v]
  for x,y,z in self.v:
   if 'River' in name:uv=abs(x-center(y))/width(y)
   elif 'Lake' in name or 'Pond' in name:uv=math.hypot(x,y)/100
   else:uv=x/200
   lines.append(f'vt {uv:.5f} {y/200:.5f}')
  for mat,ids in self.faces:lines+=['usemtl '+mat,'f '+' '.join(str(i)+'/'+str(i) for i in ids)]
  path=OUT/(name+'.obj');path.write_text('\n'.join(lines));return {'name':name,'file':str(path)}
manifest=[]
for variant in range(2):
 m=Mesh();rings=[];n=10
 for z,r in [(0,.55),(20,.9),(65,1),(100,.68),(114,.2)]:
  rings.append([(math.cos(i*math.tau/n)*r*(70+variant*12)*(1+.07*math.sin(i*3+variant)),math.sin(i*math.tau/n)*r*64,z+5*math.sin(i*2+variant)) for i in range(n)])
 for j in range(len(rings)-1):
  for i in range(n):k=(i+1)%n;m.poly([rings[j][i],rings[j][k],rings[j+1][k],rings[j+1][i]],'Moss' if j==3 else ('StoneLight' if (i+j)%4==0 else 'Stone'))
 m.poly(rings[-1],'Moss');manifest.append(m.save('SM_ForestCartoonRock_'+str(variant)))
m=Mesh();n=12
for i in range(n):
 a=i*math.tau/n;b=(i+1)*math.tau/n
 m.poly([(-140,math.cos(a)*48,55+math.sin(a)*48),(140,math.cos(a)*48,55+math.sin(a)*48),(140,math.cos(b)*48,55+math.sin(b)*48),(-140,math.cos(b)*48,55+math.sin(b)*48)],'Timber' if i%3 else 'Plank')
for x in [-141,141]:
 for inner,outer,mat in [(0,20,'Cream'),(20,25,'Plank'),(25,35,'Cream'),(35,40,'Plank'),(40,47,'PlankLight')]:
  for i in range(n):
   a=i*math.tau/n;b=(i+1)*math.tau/n;m.poly([(x,math.cos(a)*inner,55+math.sin(a)*inner),(x,math.cos(a)*outer,55+math.sin(a)*outer),(x,math.cos(b)*outer,55+math.sin(b)*outer),(x,math.cos(b)*inner,55+math.sin(b)*inner)],mat)
manifest.append(m.save('SM_ForestCartoonLog'))
for name,phase,n in [('SM_ForestLake',.6,48),('SM_ForestPond_A',1.8,32),('SM_ForestPond_B',3.1,32)]:
 m=Mesh()
 def ring(radius,z=0):return [(math.cos(i*math.tau/n)*radius*(1+.09*math.sin(i*math.tau/n*3+phase)+.05*math.sin(i*math.tau/n*5)),math.sin(i*math.tau/n)*radius*(1+.07*math.cos(i*math.tau/n*4+phase)),z) for i in range(n)]
 for lo,hi,mat in [(0,58,'DeepWater'),(58,82,'MidWater'),(82,100,'ShallowWater'),(100,109,'Shore')]:
  a=ring(lo);b=ring(hi)
  for i in range(n):k=(i+1)%n;m.poly([a[i],b[i],b[k],a[k]],mat)
 manifest.append(m.save(name))
def center(y):return 180*math.sin(y/1200)+90*math.sin(y/470)
def width(y):return 130+25*math.sin(y/700+.4)
m=Mesh();ys=list(range(-5800,4401,160))
for y1,y2 in zip(ys,ys[1:]):
 for lo,hi,mat in [(-1.35,-1,'Shore'),(-1,-.7,'ShallowWater'),(-.7,0,'DeepWater'),(0,.7,'DeepWater'),(.7,1,'ShallowWater'),(1,1.35,'Shore')]:
  m.poly([(center(y1)+lo*width(y1),y1,0),(center(y1)+hi*width(y1),y1,0),(center(y2)+hi*width(y2),y2,0),(center(y2)+lo*width(y2),y2,0)],mat)
manifest.append(m.save('SM_ForestRiver'))
palette={'DeepWater':(.018,.11,.16),'MidWater':(.025,.19,.24),'ShallowWater':(.05,.28,.29),'Shore':(.13,.23,.105),'Stone':(.35,.36,.29),'StoneLight':(.46,.45,.35),'Moss':(.25,.37,.12),'Timber':(.28,.135,.065),'Plank':(.46,.28,.13),'PlankLight':(.57,.37,.19),'Cream':(.74,.66,.43)}
lines=[]
for name,rgb in palette.items():lines+=['newmtl '+name,'Kd '+' '.join(map(str,rgb)),'Ka 0 0 0','Ks 0 0 0','d 1','illum 2']
(OUT/'ForestFeatures.mtl').write_text('\n'.join(lines));(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('CARTOON_PROPS_AND_ORGANIC_WATER_ASSETS_READY')

# Keep the hand-shaped rounded log source when regenerating other forest features.
exec(compile((ROOT/'Scripts/build_cartoon_logs.py').read_text(),'build_cartoon_logs.py','exec'))
