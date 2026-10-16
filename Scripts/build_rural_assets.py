"""Original low-poly timber/fieldstone village assets; centimetres, editable OBJ."""
from pathlib import Path
import math,random,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'ContentSource/RuralVillage';OUT.mkdir(parents=True,exist_ok=True)
PALETTE={'Timber':(.28,.135,.065),'Plank':(.46,.28,.13),'PlankLight':(.57,.37,.19),'Shingle':(.26,.18,.10),'ShingleLight':(.35,.24,.12),'Stone':(.35,.36,.29),'StoneLight':(.46,.45,.35),'Iron':(.09,.10,.08),'Glass':(.65,.48,.19),'Cream':(.74,.66,.43),'Moss':(.25,.37,.12),'Soil':(.22,.13,.065),'Crop':(.33,.48,.12),'Wheat':(.66,.48,.16)}
manifest=[]
class Mesh:
 def __init__(self):self.v=[];self.f=[]
 def poly(self,points,mat):
  n=len(self.v);self.v.extend(points);self.f.append((mat,list(range(n+1,n+len(points)+1))))
 def box(self,c,s,mat):
  x,y,z=c;a,b,d=[n/2 for n in s]
  p=[(x-a,y-b,z-d),(x+a,y-b,z-d),(x+a,y+b,z-d),(x-a,y+b,z-d),(x-a,y-b,z+d),(x+a,y-b,z+d),(x+a,y+b,z+d),(x-a,y+b,z+d)]
  for face in [(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]:self.poly([p[i] for i in face],mat)
 def cylinder(self,c,r,h,mat,n=8):
  x,y,z=c;bottom=[(x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n),z-h/2) for i in range(n)];top=[(a,b,z+h/2) for a,b,_ in bottom]
  self.poly(bottom[::-1],mat);self.poly(top,mat)
  for i in range(n):j=(i+1)%n;self.poly([bottom[i],bottom[j],top[j],top[i]],mat)
 def save(self,name):
  lines=['mtllib RuralVillage.mtl','o '+name]+[f'v {x:.3f} {-y:.3f} {z:.3f}' for x,y,z in self.v]
  # A simple per-face mapping keeps the source useful for later texture work.
  lines+=['vt 0 0','vt 1 0','vt 1 1','vt 0 1']
  for mat in PALETTE:
   lines.append('usemtl '+mat)
   for m,f in self.f:
    if m==mat:lines.append('f '+' '.join(f'{index}/{i%4+1}' for i,index in enumerate(f)))
  path=OUT/(name+'.obj');path.write_text('\n'.join(lines));manifest.append({'name':name,'file':str(path),'faces':len(self.f)})

def house(name,w,d,h,peak,seed,porch=False,guild=False,barn=False):
 rng=random.Random(seed);m=Mesh();base=38;door=160 if guild else 120
 # Individual fieldstones and horizontal boards give modest, handmade walls.
 for y in [-d/2,d/2]:
  for i in range(math.ceil(w/75)):
   x=-w/2+(i+.5)*w/math.ceil(w/75)
   if y>0 and abs(x)<door/2:continue
   m.box((x,y,base/2),(w/math.ceil(w/75)-4,42,base-3),rng.choice(['Stone','StoneLight']))
 for x in [-w/2,w/2]:
  for i in range(math.ceil(d/75)):m.box((x,-d/2+(i+.5)*d/math.ceil(d/75),base/2),(42,d/math.ceil(d/75)-4,base-3),rng.choice(['Stone','StoneLight']))
 rows=math.ceil(h/24)
 for row in range(rows):
  z=base+(row+.5)*h/rows
  m.box((0,-d/2,z),(w,17,h/rows-2),rng.choice(['Plank','PlankLight']))
  for side in [-1,1]:m.box((side*w/2,0,z),(17,d,h/rows-2),rng.choice(['Plank','PlankLight']))
  if z<base+205:
   for side in [-1,1]:m.box((side*(w+door)/4,d/2,z),((w-door)/2,17,h/rows-2),rng.choice(['Plank','PlankLight']))
  else:m.box((0,d/2,z),(w,17,h/rows-2),rng.choice(['Plank','PlankLight']))
 for x in [-w/2,0,w/2]:
  for y in [-d/2,d/2]:
   if x==0 and y>0:continue
   m.box((x,y,base+h/2),(23,27,h+16),'Timber')
 for y in [-d/2,d/2]:m.box((0,y,base+h),(w+34,30,26),'Timber')
 # Solid gables and staggered wooden shingle strips, rather than city tiles.
 for y in [-d/2,d/2]:m.poly([(-w/2,y,base+h),(w/2,y,base+h),(0,y,peak)],'Plank')
 eave=w/2+45;edgeZ=base+h-15;ridge=peak+15
 for side in [-1,1]:
  for row in range(8):
   a=row/8;b=(row+1)/8;xa=side*eave*a;xb=side*eave*b;za=ridge+(edgeZ-ridge)*a;zb=ridge+(edgeZ-ridge)*b
   for col in range(math.ceil((d+90)/75)):
    ya=-d/2-45+col*(d+90)/math.ceil((d+90)/75);yb=ya+(d+90)/math.ceil((d+90)/75)-2
    m.poly([(xa,ya,za+2),(xb,ya,zb+2),(xb,yb,zb+2),(xa,yb,za+2)],rng.choice(['Shingle','ShingleLight']))
  m.poly([(0,-d/2-46,ridge),(side*eave,-d/2-46,edgeZ),(side*eave,-d/2-40,edgeZ-13),(0,-d/2-40,ridge-13)],'Timber')
 m.box((0,0,ridge),(24,d+105,18),'Timber')
 # Restrained wooden-framed windows with dusk-controlled glass.
 windows=[]
 for x in [-w*.31,w*.31]:
  y=d/2+13;z=base+h*.56;windows.append((x,y,z))
  m.box((x,y,z),(95,10,105),'Iron');m.box((x,y+6,z),(78,9,88),'Glass')
  for dx in [-48,0,48]:m.box((x+dx,y+14,z),(8,13,110),'Timber')
  for dz in [-53,0,53]:m.box((x,y+14,z+dz),(105,13,8),'Timber')
  m.box((x,y+23,z-59),(119,42,13),'PlankLight')
 m.box((0,d/2+8,base+211),(door+28,28,22),'Timber')
 for x in [-door/2-6,door/2+6]:m.box((x,d/2+8,base+100),(18,25,210),'Timber')
 for step in range(2):m.box((0,d/2+52+step*35,base-(step+1)*13),(door+75,85,17),'Stone')
 # One small fieldstone chimney, slightly crooked from block to block.
 for k in range(8):m.box((w*.29+(k%2)*3,-d*.22,peak-100+k*28),(78,78,26),'StoneLight' if k%3==0 else 'Stone')
 m.box((w*.29,-d*.22,peak+109),(94,94,14),'Stone')
 if porch:
  m.box((-w*.3,d/2+100,25),(w*.42,210,20),'Plank')
  for x in [-w*.5,-w*.1]:m.box((x,d/2+180,139),(18,18,230),'Timber')
  m.poly([(-w*.52,d/2+5,h*.82),(-w*.08,d/2+5,h*.82),(-w*.08,d/2+210,h*.65),(-w*.52,d/2+210,h*.65)],'Shingle')
 if guild:
  m.box((0,d/2+28,base+h+6),(255,26,70),'Timber')
  m.box((0,d/2+44,base+h+6),(235,8,52),'PlankLight')
  m.box((-w*.40,d/2+88,100),(125,24,150),'Timber')
  m.box((-w*.40,d/2+104,110),(105,8,115),'Cream')
 if barn:
  for x in [-w*.35,w*.35]:m.box((x,d/2+90,68),(90,90,100),'Wheat')
 m.save(name);return {'width':w,'depth':d,'height':peak+120,'door':door,'windows':windows}

specs={}
specs['SM_RuralCottage_A']=house('SM_RuralCottage_A',570,440,235,410,17,porch=True)
specs['SM_RuralCottage_B']=house('SM_RuralCottage_B',640,470,255,445,25)
specs['SM_RuralCottage_C']=house('SM_RuralCottage_C',480,410,235,395,40,porch=True)
specs['SM_RuralGuildHall']=house('SM_RuralGuildHall',900,650,310,540,51,guild=True)
specs['SM_RuralBarn']=house('SM_RuralBarn',720,640,280,500,62,barn=True)
m=Mesh()
for i in range(6):m.box((10+i*20,0,110),(18,13,205),'PlankLight' if i%2 else 'Plank')
for z in [45,165]:m.box((60,9,z),(116,8,15),'Timber')
m.cylinder((104,17,108),5,12,'Iron');m.save('SM_RuralDoor')
m=Mesh()
for x in [-95,95]:m.box((x,0,60),(17,18,120),'Timber')
for z in [42,88]:m.box((0,0,z),(205,13,12),'PlankLight')
m.save('SM_RuralFence')
m=Mesh()
for row in range(3):
 for i in range(12):
  a=(i+(row%2)*.5)*math.tau/12;m.box((math.cos(a)*85,math.sin(a)*85,row*26+15),(42,40,24),'StoneLight' if i%3==0 else 'Stone')
for x in [-110,110]:m.box((x,0,130),(22,24,255),'Timber')
m.box((0,0,265),(260,28,25),'Timber')
m.poly([(-155,-95,240),(155,-95,240),(155,0,315),(-155,0,315)],'Shingle')
m.poly([(-155,0,315),(155,0,315),(155,95,240),(-155,95,240)],'ShingleLight')
m.cylinder((0,0,95),2,160,'Cream');m.cylinder((0,0,32),24,35,'Plank');m.save('SM_RuralWell')
m=Mesh()
for x in [-55,55]:
 for y in [-22,22]:m.box((x,y,23),(12,12,46),'Timber')
for y in [-23,0,23]:m.box((0,y,50),(155,21,12),'PlankLight')
m.save('SM_RuralBench')
m=Mesh()
for i in range(7):
 a=i*math.tau/7;m.poly([(0,0,8),(math.cos(a-.35)*24,math.sin(a-.35)*24,17),(math.cos(a)*33,math.sin(a)*33,37),(0,0,43)],'Crop' if i%2 else 'Moss')
m.cylinder((0,0,20),14,30,'Crop');m.save('SM_RuralCabbage')
m=Mesh()
for i in range(5):
 x=(i%3-1)*12;y=(i//3-.5)*18;m.box((x,y,29),(3,3,58),'Wheat')
 for k in range(3):m.cylinder((x,y,58+k*6),5-k,7,'Wheat',5)
m.save('SM_RuralWheat')
(OUT/'RuralVillage.mtl').write_text('\n'.join('newmtl '+k+'\nKd '+' '.join(map(str,c)) for k,c in PALETTE.items()))
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
(OUT/'buildings.json').write_text(json.dumps(specs,indent=2))
(OUT/'palette.json').write_text(json.dumps(PALETTE,indent=2))
print('RURAL_ASSETS_BUILT '+str(len(manifest)))
